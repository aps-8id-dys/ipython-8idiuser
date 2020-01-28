logger.info(__file__)

"""
local, custom Bluesky plans (scans)

Classes and Other Structures

    insert_remove_tuple
    Presets

Variables

    presets
    PV_REG_MAP

Plans

    AD_Acquire
    bb
    beam_params_backup
    beam_params_restore
    blockbeam
    block_directbeam_common
    insert_diodes
    insert_flux_pind
    insert_pind1
    insert_pind2
    lineup
    movesample
    movesamx
    movesamz
    pv_reg_write
    remove_diodes
    remove_flux_pind
    remove_pind1_out
    remove_pind2
    sb
    select_LAMBDA
    select_RIGAKU
    showbeam
    tw (not implemented yet)

Functions

    calc_flux
    flux
    flux_params
    get_detector_number_by_name
    print_flux_params
    pv_reg_read
    taylor_series

"""


# access by subscript or by name (obj[0]= same as obj.insert)
# NOTE: "in" is a Python keyword that cannot be re-used
insert_remove_tuple = namedtuple('insert_remove_tuple', 'insert remove')

class Presets:
    """
    various instrument settings and constants
    """
    pind1 = insert_remove_tuple(1, 0)
    pind2 = insert_remove_tuple(1, 0)
    flux = insert_remove_tuple(1, 0)

presets = Presets()

PV_REG_MAP = {
    "template": "8idi:Reg%d",
    "detector_pv" : "8idi:Reg2",
    "registers/detector": 10,
    "highest register": 200,
    "regpv_start": {
        "current" : 11,
        "LAMBDA" : 91,
        "RIGAKU500K_NoGap" : 141,
    },
    "detectors" : {
        25 : "LAMBDA",
        46 : "RIGAKU500K_NoGap",
    },
    "burst mode pv" : "8idi:Reg124",    # added May 2019
}
PV_REG_MAP["registers"] = [     # each register is a signal
    EpicsSignal(
        PV_REG_MAP["template"] % (i+1), 
        name="pv_reg%d" % (i+1)
        )
    for i in range(PV_REG_MAP["highest register"])
    ]
PV_REG_MAP["registers"].insert(0, None)     # offset since no 8idi:Reg0


# Bluesky plans to move the diodes in/out

def insert_diodes():
    "insert ALL the diodes"
    yield from bps.mv(
        actuator_pind1, presets.pind1.insert,
        actuator_pind2, presets.pind2.insert,
        actuator_flux, presets.flux.insert,
    )
    logger.debug(f"inserted all PIN diodes")

def remove_diodes():
    "remove ALL the diodes"
    yield from bps.mv(
        actuator_pind1, presets.pind1.remove,
        actuator_pind2, presets.pind2.remove,
        actuator_flux, presets.flux.remove,
    )
    logger.debug(f"removed all PIN diodes")

def insert_pind1():
    yield from bps.mv(actuator_pind1, presets.pind1.insert)
    logger.debug(f"inserted pind1")

def remove_pind1():
    yield from bps.mv(actuator_pind1, presets.pind1.remove)
    logger.debug(f"removed pind1")

def insert_pind2():
    yield from bps.mv(actuator_pind2, presets.pind2.insert)
    logger.debug(f"inserted pind2")

def remove_pind2():
    yield from bps.mv(actuator_pind2, presets.pind2.remove)
    logger.debug(f"removed pind2")

def insert_flux_pind():
    yield from bps.mv(actuator_flux, presets.flux.insert)
    logger.debug(f"inserted flux pind")

def remove_flux_pind():
    yield from bps.mv(actuator_flux, presets.flux.remove)
    logger.debug(f"removed flux pind")


# alignment plans

def lineup(counter, axis, minus, plus, npts, time_s=0.1, peak_factor=4, width_factor=0.8,_md={}):
    """
    lineup and center a given axis, relative to current position

    PARAMETERS
    
    counter : Signal or scaler channel object
        detector or Signal to be maximized
    
    axis : movable
        Signal or EpicsMotor to use for alignment, the independent axis
    
    minus : float
        first point of scan at this offset from starting position
    
    plus : float
        last point of scan at this offset from starting position
    
    npts : int
        number of data points in the scan
    
    time_s : float (default: 0.1)
        count time per step
    
    peak_factor : float (default: 4)
        maximum must be greater than 'peak_factor'*minimum
    
    width_factor : float (default: 0.8)
        fwhm must be less than 'width_factor'*plot_range

    EXAMPLE:

        RE(lineup(diode, foemirror.theta, -30, 30, 30, 1.0))
    """
     # first, determine if counter is part of a ScalerCH device
    scaler = None
    obj = counter.parent
    if isinstance(counter.parent, ScalerChannel):
        if hasattr(obj, "parent") and obj.parent is not None:
            obj = obj.parent
            if hasattr(obj, "parent") and isinstance(obj.parent, ScalerCH):
                scaler = obj.parent

    if scaler is not None:
        old_sigs = scaler.stage_sigs
        scaler.stage_sigs["preset_time"] = time_s
        scaler.select_channels([counter.name])

    if hasattr(axis, "position"):
        old_position = axis.position
    else:
        old_position = axis.value

    def peak_analysis():
        aligned = False
        if counter.name in bec.peaks["cen"]:
            table = pyRestTable.Table()
            table.labels = ("key", "value")
            table.addRow(("axis", axis.name))
            table.addRow(("detector", counter.name))
            table.addRow(("starting position", old_position))
            for key in bec.peaks.ATTRS:
                table.addRow((key, bec.peaks[key][counter.name]))
            logger.info(f"alignment scan results:\n{table}")

            lo = bec.peaks["min"][counter.name][-1]  # [-1] means detector
            hi = bec.peaks["max"][counter.name][-1]  # [0] means axis
            fwhm = bec.peaks["fwhm"][counter.name]
            final = bec.peaks["cen"][counter.name]

            ps = list(bec._peak_stats.values())[0][counter.name]    # PeakStats object
            # get the X data range as received by PeakStats
            x_range = abs(max(ps.x_data) - min(ps.x_data))

            if final is None:
                logger.error(f"centroid is None")
                final = old_position
            elif fwhm is None:
                logger.error(f"FWHM is None")
                final = old_position
            elif hi < peak_factor*lo:
                logger.error(f"no clear peak: {hi} < {peak_factor}*{lo}")
                final = old_position
            elif fwhm > width_factor*x_range:
                logger.error(f"FWHM too large: {fwhm} > {width_factor}*{x_range}")
                final = old_position
            else:
                aligned = True
            
            logger.info(f"moving {axis.name} to {final}  (aligned: {aligned})")
            yield from bps.mv(axis, final)
        else:
            logger.error("no statistical analysis of scan peak!")
            yield from bps.null()

        # too sneaky?  We're modifying this structure locally
        bec.peaks.aligned = aligned
        bec.peaks.ATTRS =  ('com', 'cen', 'max', 'min', 'fwhm')

    md = dict(_md)
    md["purpose"] = "alignment"
    yield from bp.rel_scan([counter], axis, minus, plus, npts, md=md)
    yield from peak_analysis()

    if bec.peaks.aligned:
        # again, tweak axis to maximize
        md["purpose"] = "alignment - fine"
        fwhm = bec.peaks["fwhm"][counter.name]
        yield from bp.rel_scan([counter], axis, -fwhm, fwhm, npts, md=md)
        yield from peak_analysis()

    if scaler is not None:
        scaler.select_channels()
        scaler.stage_sigs = old_sigs


def calc_flux(cps, params, pin_diode):
    """
    calculate the number of photons/s from diode count rate
    """
    gain = preamps.gains[pin_diode.name]
    amps = (cps/params["CtpV"])*gain
    photons = amps/(1.60218e-19*params["N_elec"]*params["Abs_frac"])
    return photons


def flux(pin_diode, count_rate):
    """
    print the flux on the named photodiode
    """
    gain = preamps.gains[pin_diode.name]
    params = flux_params(pin_diode)
    print_flux_params(params, pin_diode)

    t = pyRestTable.Table()
    t.addLabel("term")
    t.addLabel("value")
    t.addRow(("diode", pin_diode.name))
    t.addRow(("count rate, cps", count_rate))
    t.addRow(("photo current, A", count_rate/params["CtpV"]*gain))
    v = calc_flux(count_rate, params, pin_diode)
    t.addRow(("flux, ph/s", f"{v:8.3g}"))

    logger.info(f"\n{t}")

    return v


def taylor_series(x, coefficients):
    """
    compute a Taylor series expansion at x
    
    a0 + x*(a1 + x*(a2+x*0)
    """
    v = 0
    for a in reversed(coefficients):
        v = v*x + a
    return v


def flux_params(_counter):
    """
    dictionary of computed conversion constants
    """
    result = {}
    result["Amps_per_Volt"] = preamps.gains[_counter.name]   # amplifier gain
    result["CtpV"] = 1e5                        # voltage/frequency conversion
    Length = result["fluxLength"] = 0.04        #
    result["Element"] = "Si"
    keV = monochromator.energy.position
    result["Ephot"] = keV * 1000

    if result["Element"] == "Ar":
        N_elec = result["Ephot"]/26.4
        v = taylor_series(keV, [-2.78262, .782515, -.0379763, 1.04293e-3, -1.14407e-5])
        Elength =  math.exp(v)
    elif result["Element"] == "N2":
        N_elec = result["Ephot"]/34.8
        v = taylor_series(keV, [6.17639, -6.90647e-1, 2.44039e-2, -.453977e-3, 0.033084e-4])
        Elength = 1.0/(math.exp(v)*1.165e-3)
    elif result["Element"] == "He":
        N_elec = result["Ephot"]/41.3
        v = taylor_series(keV, [15.4707, 0.972059, -0.0487191, 0.00134312, -1.46011e-05])
        Elength = math.exp(v) / 1e4
    elif result["Element"] == "Si":
        N_elec = result["Ephot"]/3.62   # 3.62: electron-hole pair production energy
        Elength = 61e-4*pow((7.65/keV),-3)
        Length = 400e-4
    else:
        raise KeyError(f"flux params not defined for '{result['Element']}'")

    result["N_elec"] = N_elec
    result["Elength"] = Elength
    result["Abs_frac"] = (1-math.exp(-Length/Elength))

    return result


def print_flux_params(params, counter):
    gain = preamps.gains[counter.name]
    element = params['Element']
    t = pyRestTable.Table()
    t.addLabel("term")
    t.addLabel("value")
    t.addLabel("units")
    t.addRow(("detector", counter.name, ""))
    t.addRow(("Amps/Volt", gain, "A/V"))
    t.addRow(("counts/Volt", params["CtpV"], ""))
    t.addRow(("Length", params["fluxLength"], "cm"))
    t.addRow(("Element", element, ""))
    t.addRow(("Ephot", params["Ephot"], "eV"))
    t.addRow((f"{element} detector", params["Elength"], "cm"))
    logger.info(f"\n{t}")


def bb():
    """block beam"""
    yield from bps.mv(shutter, "close")

blockbeam = bb  # alias

def sb():
    """show beam"""
    yield from bps.mv(shutter, "open")

showbeam = sb   # alias

def block_directbeam_common():
    yield from bps.mv(
        att1, 15,
        att2, 15,
    )


def tw(counter, motor, delta):
    """
    maximize a positioner using a motor and reading a scaler channel

    In SPEC, the `tw` command initiates an interactive session.
    Automate that here, if possible.
    """
    # Usage:  tw mot [mot2 ...] delta [delta2 ...] [count_time]
    raise NotImplementedError("Need to write the Bluesky tw() plan")

# -----------------------------------------------------------------------

def get_detector_number_by_name(detName):
    if detName in PV_REG_MAP["detectors"].values():
        for detNum, k in PV_REG_MAP["detectors"].items():
            if k == detName:
                return detNum


def pv_reg_read(num):
    """read a value from PV register (indexed by number)"""
    register = PV_REG_MAP["registers"][num]
    if register is not None:
        return register.value


def pv_reg_write(num, value):
    """read a value to PV register (indexed by number)"""
    register = PV_REG_MAP["registers"][num]
    if register is not None:
        yield from bps.mv(register, value)


def beam_params_backup():
    """
    copy detector registers from current to detector
    """
    detNum = dm_pars.detNum.value
    detName = PV_REG_MAP["detectors"].get(detNum)

    if detName is None:
        msg = f"Unknown detector number {detNum}"
        msg += f" in EPICS PV register {dm_pars.detNum.pvname}"
        raise ValueError(msg)

    offset = PV_REG_MAP["regpv_start"][detName]
    offset_current = PV_REG_MAP["regpv_start"]["current"]
    t = pyRestTable.Table()
    t.addLabel("value")
    t.addLabel("from")
    t.addLabel("to")
    for i in range(PV_REG_MAP["registers/detector"]):
        target = PV_REG_MAP["registers"][i + offset]
        source = PV_REG_MAP["registers"][i + offset_current]
        t.addRow((source.get(), source.pvname, target.pvname))
        yield from bps.mv(target, source.get())
    logger.debug(f"Detector {detName} Beam Params are Backed up\n{t}")


def beam_params_restore():
    """
    copy detector registers from detector to current
    """
    detNum = dm_pars.detNum.value
    detName = PV_REG_MAP["detectors"].get(detNum)

    if detName is None:
        msg = f"Unknown detector number {detNum}"
        msg += f" in EPICS PV register {dm_pars.detNum.pvname}"
        raise ValueError(msg)

    offset = PV_REG_MAP["regpv_start"][detName]
    offset_current = PV_REG_MAP["regpv_start"]["current"]
    t = pyRestTable.Table()
    t.addLabel("value")
    t.addLabel("from")
    t.addLabel("to")
    for i in range(PV_REG_MAP["registers/detector"]):
        source = PV_REG_MAP["registers"][i + offset]
        target = PV_REG_MAP["registers"][i + offset_current]
        t.addRow((source.get(), source.pvname, target.pvname))
        yield from bps.mv(target, source.get())
        # logger.debug(f"{target.pvname} = {target.value}")
    logger.debug(f"Detector {detName} Beam Params are restored\n{t}")


def select_LAMBDA(distance=None):
    """
    select the LAMBDA detetcor
    """
    yield from beam_params_backup()
    yield from bps.mv(
        dm_pars.detNum, get_detector_number_by_name("LAMBDA"),
        dm_pars.detector_distance, 3930.00, #moved sample 7 inches closer to detector
        dm_pars.airgap, 240.00,
    )
    # logger.info(f"******** detector number {dm_pars.detNum.value} ************************")
    yield from beam_params_restore()
    yield from bps.sleep(1)
    yield from blockbeam()
    
    logger.info("Moving LAMBDA PAD to the direct beam position")

    distance = distance or "4 m"
    if distance == "4 m":
        # logger.debug(f"ccdx0={dm_pars.ccdx0.value}, ccdz0={dm_pars.ccdz0.value}")
        yield from bps.mv(
            detu.x, dm_pars.ccdx0.get(),
            detu.z, dm_pars.ccdz0.get(),
        )
        # yield from bps.mv(
        #     detu.x, 214.10,
        #     detu.z, 36.95,
        # )
        # logger.debug(f"detu.x={detu.x.position}, detu.z={detu.z.position}")
    elif distance == "8 m":
        yield from bps.mv(
            detd.x, dm_pars.ccdx0.get(),
            detd.z, dm_pars.ccdz0.get(),
        )
        # yield from bps.mv(
        #     detd.x, 127.53,
        #     detd.z, 15.55,
        # )

    yield from bps.mv(shutter_override, 1)
    yield from blockbeam()

    yield from bps.mv(
        # NOTE: these are all stringout records!  Use a str!
        soft_glue.send_ext_pulse_tr_sig_to_trig, "1",
        # soft_glue.set_shtr_sig_pulse_tr_mode, "0",
        # soft_glue.send_det_sig_pulse_tr_mode, "0",
    )

	# TODO: needs some planning here, see below
    # def xpcs_pre_start \'xpcs_pre_start_LAMBDA\';
	# def user_xpcs_loop \'user_xpcs_loop_LAMBDA\';

    yield from bps.mv(shutter_mode, "1UFXC")    # "align" mode

    dm_workflow.transfer = "xpcs8-01-Lambda"
    dm_workflow.analysis = "xpcs8-02-Lambda"
    yield from bps.mv(
        dm_pars.burst_mode_state, 0,    # 2019-05, set default status
        dm_pars.transfer, dm_workflow.transfer,
        dm_pars.analysis, dm_workflow.analysis,
    )


def select_RIGAKU():
    """
    select the RIGAKU detetcor
    """
    yield from beam_params_backup()
    yield from bps.mv(
        dm_pars.detNum, get_detector_number_by_name("RIGAKU500K_NoGap"),
        dm_pars.detector_distance, 3930.00, #moved sample 7 inches closer to detector
        dm_pars.airgap, 100.00,
    )
    logger.info(f"******** detector number {dm_pars.detNum.value} ************************")
    yield from beam_params_restore()
    yield from bps.sleep(1)
    yield from blockbeam()
    
    logger.info("Moving RIGAKU to the direct beam position")

    # logger.debug(f"ccdx0={dm_pars.ccdx0.value}, ccdz0={dm_pars.ccdz0.value}")
    yield from bps.mv(
        detu.x, dm_pars.ccdx0.get(),
        detu.z, dm_pars.ccdz0.get(),
    )
    # logger.debug(f"detu.x={detu.x.position}, detu.z={detu.z.position}")

    yield from bps.mv(shutter_override, 1)
    yield from blockbeam()

    # TODO: needs some planning here, see below
    # def xpcs_pre_start \'xpcs_pre_start_RIGAKU\';
    # def user_xpcs_loop \'user_xpcs_loop_RIGAKU\';

    dm_workflow.transfer = "xpcs8-01"
    dm_workflow.analysis = "xpcs8-02-Rigaku-bin"
    yield from bps.mv(
        dm_pars.burst_mode_state, 0,    # 2019-05, set default status
        dm_pars.transfer, dm_workflow.transfer,
        dm_pars.analysis, dm_workflow.analysis,
    )


def movesample():
    yield from samplestage.movesample()


def movesamx():
    yield from samplestage.movesamx()


def movesamz():
    yield from samplestage.movesamz()


def move_pind1_in():
    yield from bps.mv(actuator_pind1, "IN")


def move_pind1_out():
    yield from bps.mv(actuator_pind1, "OUT")


def move_pind2_in():
    yield from bps.mv(actuator_pind2, "IN")


def move_pind2_out():
    yield from bps.mv(actuator_pind2, "OUT")


def move_pind4z_in():
    yield from bps.mv(actuator_flux, "IN")


def move_pind4z_out():
    yield from bps.mv(actuator_flux, "OUT")

def pre_align():
    """
    This is not a plan and so we should use it in command line, which means no use of RE
    """
    global att, default_counter
    shutter.close()
    shutter_mode.put("1UFXC")
    actuator_flux.put("IN")
    att.put(0)
    default_counter = pind4

def post_align():
    """
    This is not a plan and so we should use it in command line, which means no use of RE
    """
    global att
    shutter.close()
    #shutter_mode.put("1UFXC")
    actuator_flux.put("OUT")
    att.put(0) #att will be defined to att1 or att2

# --------------------------------------------------------------------

# TODO: do we need this SPEC code any longer?
"""
These two macros are detector-specific, as are others.

	# def xpcs_pre_start \'xpcs_pre_start_LAMBDA\'; # before a batch of scans
	# def user_xpcs_loop \'user_xpcs_loop_LAMBDA\'; # with each scan in a batch

This begs for a superclass that is used in operations where a 
subclass is defined for each detector, configured for that detector.

Also, current operations pattern is to treat each scan separately,
so that only one detector-specific macro is needed.

768.SPEC8IDI> prdef xpcs_pre_start_LAMBDA

# /home/beams/8IDIUSER/batches/2019/Oct2019/ccd_settings.do
def xpcs_pre_start_LAMBDA '{
    CCD_POLLTIME=1
#    COMPRESSION=1  ##raw=0, compressed=1
#    EXT_TRIGGER=0 ##use 0 or 2, do not use 1 for now
#    LAMBDA_OPERATING_MODE = 0;
    epics_put("8idi:Reg8",COMPRESSION)
    CCD_THROW= 0  # must be zero for non-compressed mode
    COPY_LOCAL_DATA=1  ############
    COPY_LOCAL_DATA_M2=0  ############
    PRINT_HARDCOPY_LOGFILE = 0
    WRITE_LOCAL=2 ##If set to >0, save batchinfo locally, data on local disk, set to 2 will copy over
    plcounter ccdc
}'

769.SPEC8IDI> prdef user_xpcs_loop_LAMBDA

# /home/beams/8IDIUSER/batches/2019/Oct2019/ccd_settings.do
def user_xpcs_loop_LAMBDA '{
	monitorBeamToI
	waitForFaultClear
##	takeflux vacuum 1
    movesample
#    move_rheometer
#  	movesamth
    wm samx samz samth
#    wm ti3_x ti3_z
#    wm samx samz sampit
	takeflux 1
}'

770.SPEC8IDI> prdef takeflux

# /home/beams/S8SPEC/spec/macros/sites/spec8IDI/site_f.mac
def takeflux '{
  ##A new pneumatic feedthrough with a 20 mm PIN diode has been mounted at the
  ##longitudinal location of the beam stop and at 90 degrees. This feedthrough 
  ##will esp. make flux measurement in reflection geometry very quick (3 min 
  ##reduced to 3 sec).(Suresh, Feb.11,2008)

  # Usage: takeflux [vacuum] [time]
  local i bg cfield cps ctime curnt dt flx ifield nflx params xtime Monitor_flux
  local sz sx sth
  {
    rdef batch_cleanup \'{
      emptydef batch_cleanup
      blockbeam; shutteron; waitmove
      }\'
    preamp_setread;
    params = flux_params("pind4")
    if ("$1" == "vacuum") {
      printf("\nTakeflux: Moving samx to %g, samz to %g\n",\
             samxvac, samzvac)
      umv samx samxvac; umv samz samzvac;
     ##The function move_pind4z_in and out are defined in pind_positions_8idi.mac
     move_pind4z_in
     waitmove; 
      }
    else {
     ##The function move_pind4z_in and out are defined in pind_positions_8idi.mac
      move_pind4z_in
       waitmove;sleep(0.1)
      # leave sample wherever it is already
      }
    if ($# > 1) xtime = $2
    else if ($# && "$1" != "vacuum") xtime = $1
    else xtime = 5 
    printf("Measuring background:\n")
    p date();
    blockbeam; waitmove;sleep(0.1)
    uct xtime
    ctime = (S[sec]) ? S[sec] : xtime
#    bg = S[DET]/ctime
#hard coded the detector to "pind4" since not defining the counter before 
#running the ccd_batch always causes the wrong detector to be used for 
#flux (Suresh, June 2004, onset of Epics in 8-ID-I)
    bg = S[pind4]/ctime
    curnt = epics_get("S:SRcurrentAI")
    printf("Ring Current = %6.2f mA\n",curnt)
    printf("Measuring intensity:\n")
    p date();
    shutteroff_default; showbeam; waitmove;sleep(0.1)
    uct xtime
    blockbeam; shutteron;
     ##The function move_pind4z_in and out are defined in pind_positions_8idi.mac
    move_pind4z_out
    waitmove;sleep(.1)
    ctime = (S[sec]) ? S[sec] : xtime
#    cps = S[DET]/ctime - bg
    cps = S[pind4]/ctime - bg
    Monitor_flux = epics_get("8idi:scaler1_calc1.H")/ctime 

    if (cps > 650000) {
                       for (i=1;i<11;i++) {
                           beep;sleep(1);
    			   printf("\nWarning: Counts is very close to saturation of pind4, Check the Sensitivity:\n");
                       }
    }

    printf("%g cps is a current of %g Amps \n",cps,\
          (cps/params["CtpV"])*params["Amps_per_Volt"])

    flx = calc_flux(cps,params,"pind4")
    if (curnt) nflx = calc_flux(cps*100/curnt,params,"pind4")
    printf("%8.3g photons per second \n",flx)
    if (nflx) printf("%8.3g photons per second per 100 mA \n",nflx)
    # make sure the parameters will be in the .batchinfo file
    if (!exists("batch_pars","Amps_per_Volt")) {
      for (field in params) batch_pars[field] = params[field]
      batch_pars["Element"] = inquotes(params["Element"])
      }
    if ("$1" == "vacuum") {
      add_batch_par ring_i_vacuum curnt
      add_batch_par beam_i_vacuum flx
      if (curnt) batch_pars["norm_vac_flux"] = flx/curnt
      fprintf(SHORTFILE,"\nAt samx = %g, samz = %g, samth = %g",A[samx],A[samz],A[samth])
      fprintf(SHORTFILE," (through vacuum):\n")
      fprintf(SHORTFILE,"\t%4.3g photons/sec at %5.2f mA",\
              flx,curnt)
      if (nflx) fprintf(SHORTFILE," (%4.3g per 100 mA)",nflx)
      }
    else { # sample
      sth = A[samth]; sz = A[samz]; sx = A[samx]; dt=inquotes(date())
      add_batch_par samth_flux sth
      add_batch_par samz_flux sz
      add_batch_par samx_flux sx
      add_batch_par ring_i_sample curnt
      add_batch_par beam_i flx
      add_batch_par beam_i_vacuum max(Monitor_flux,1.0)
      add_batch_par beam_i_time dt
      fprintf(SHORTFILE,"\t%4.3g photons/sec at %5.2f mA",flx,curnt)
      if (curnt && batch_pars["ring_i_vacuum"] && flx)
        fprintf(SHORTFILE," (a factor of %.3g absorbed)",\
                batch_pars["norm_vac_flux"]*curnt/flx)
      else if (nflx) fprintf(SHORTFILE," (%4.3g per 100 mA)",nflx)
      }
    fprintf(SHORTFILE,"\n")
    }
  emptydef batch_cleanup
  }'

771.SPEC8IDI> prdef UFXC_align_mode

# /home/beams/8IDIUSER/local_macros/CCD_macros/UFXC_shutter_logic.mac
def UFXC_align_mode '
	epics_put("8idi:softGlueC:AND-4_IN2_Signal","1UFXC");
	shutteroff;
	printf("Shutter will remain OPEN for alignment if **showbeam** is called\n");
'

772.SPEC8IDI> prdef UFXC_data_mode 

# /home/beams/8IDIUSER/local_macros/CCD_macros/UFXC_shutter_logic.mac
def UFXC_data_mode '
	epics_put("8idi:softGlueC:AND-4_IN2_Signal","UFXC");
	shutteroff;
	printf("Shutter will be controlled by UFXC if shutter is left in the **showbeam** state\n");
'

"""


# -----------------------------------------------------------------------


def AD_Acquire(areadet, 
        acquire_time=0.1, acquire_period=0.11, 
        num_images=100, file_name="A001",
        submit_xpcs_job=True,
        atten=None, path=None):
    """
    acquisition sequence initiating data management workflow

    outline of acquisition sequence:

    * define cam params such as acquire time, period, 
      num images, camera mode
    * define file plugin immout params such as file path,
      file name, num_images, file_number, capture
    * configure scaler channels for monitoring some 
      scalers and devices such as temperature
    * trigger area detector while monitoring the 
      above params
    """
    logger.info("AD_Acquire starting")
    path = path or f"/home/8-id-i/{aps_cycle}/bluesky"
    file_name = dm_workflow.cleanupFilename(file_name)
    file_path = os.path.join(path,file_name)
    if not file_path.endswith(os.path.sep):
        file_path += os.path.sep
    logger.info(f"file_path = {file_path}")
    
    atten = atten or Atten1
    assert atten in (Atten1, Atten2)

    # select the detector's number
    yield from bps.mv(dm_pars.detNum, areadet.detector_number)

    yield from areadet.cam.setup_modes(num_images)
    yield from areadet.cam.setTime(acquire_time, acquire_period)

    # Ask the devices to configure themselves for this plan.
    # no need to yield here, method does not have "yield from " calls
    scaler1.staging_setup_DM(acquire_period)
    areadet.staging_setup_DM(file_path, file_name,
            num_images, acquire_time, acquire_period)
    dm_workflow.set_xpcs_qmap_file(areadet.qmap_file)

    scaler1.select_channels(None) 
    monitored_things = [
        timebase,
        pind1,
        pind2,
        Atten1,
        Atten2,
        T_A,
        T_SET,
    ]
    """
        #Timebase,
        pind1,
        pind2,
        pind3,
        pind4,
        pdbs,
        I_APS,
        I0Mon,
        APD,
        cstar_l,
        cstar_h,
        oxygen,
        scaler1_time,
    """

    def timestamp_now():
        return datetime.datetime.now().strftime("%c").strip()

    def make_hdf5_workflow_filename():
        path = file_path
        if path.startswith("/data"):
            path = os.path.join("/", "home", "8-id-i", *path.split("/")[2:])
            logger.debug(f"modified path: {path}")
            if not os.path.exists(path):
                os.makedirs(path)
                logger.debug(f"created path: {path}")
        fname = (
            f"{file_name}"
            f"_{dm_pars.data_begin.value:04.0f}"
            f"-{dm_pars.data_end.value:04.0f}"
        )
        fullname = os.path.join(path, f"{fname}.hdf")
        suffix = 0
        while os.path.exists(fullname):
            suffix += 1
            fullname = os.path.join(path, f"{fname}__{suffix:03d}.hdf")
        if suffix > 0:
            logger.info(f"using modified file name: {fullname}")
        return fullname

    def update_metadata_prescan():
        detNum = int(dm_pars.detNum.value)
        det_pars = dm_workflow.detectors.getDetectorByNumber(detNum)
        logger.info(f"detNum={detNum}, det_pars={det_pars}")
        yield from bps.mv(
            # StrReg 2-7 in order
            dm_pars.root_folder, file_path,
        )
        # logger.debug("dm_pars.root_folder")

        yield from bps.mv(
            dm_pars.user_data_folder, os.path.dirname(file_path),   # just last item in path
        )
        # logger.debug("dm_pars.user_data_folder")

        yield from bps.mv(
            dm_pars.data_folder, file_name,
        )
        # logger.debug("dm_pars.data_folder")

        yield from bps.mv(
            dm_pars.source_begin_datetime, timestamp_now(),
        )
        # logger.debug("dm_pars.source_begin_datetime")

        yield from bps.mv(
            # Reg 121
            dm_pars.source_begin_current, aps.current.value,
            # Reg 101-110 in order
            dm_pars.roi_x1, 0,
            dm_pars.roi_x2, det_pars["ccdHardwareColSize"]-1,
            dm_pars.roi_y1, 0,
            dm_pars.roi_y2, det_pars["ccdHardwareRowSize"]-1,
            dm_pars.cols, det_pars["ccdHardwareColSize"],
            dm_pars.rows, det_pars["ccdHardwareRowSize"],
            dm_pars.kinetics_state, 0,                  # FIXME: SPEC generated this
            dm_pars.kinetics_window_size, 0,            # FIXME:
            dm_pars.kinetics_top, 0,                    # FIXME:
            dm_pars.attenuation, atten.value,
        )
        # logger.debug("Reg 121, 101-110 done")

        yield from bps.mv(
            # Reg 111-120 in order
            #dm_pars.dark_begin, -1,            #  edit if detector needs this
            #dm_pars.dark_end, -1,              #  op cit
            dm_pars.data_begin, 1,
            dm_pars.data_end, num_images,
            dm_pars.exposure_time, acquire_time,
            dm_pars.exposure_period, acquire_period,
            # dm_pars.specscan_dark_number, -1,   #  not used, detector takes no darks
            dm_pars.stage_x, detu.x.position,
            dm_pars.stage_z, detu.z.position,
        )
        # logger.debug("Reg 111-120 done")

        yield from bps.mv(
            # Reg 123-127 in order
            dm_pars.I0mon, I0Mon.value,
            dm_pars.burst_mode_state, 0,   # 0 for Lambda, other detector might use this
            dm_pars.number_of_bursts, 0,   # 0 for Lambda, other detector might use this
            dm_pars.first_usable_burst, 0,   # 0 for Lambda, other detector might use this
            dm_pars.last_usable_burst, 0,   # 0 for Lambda, other detector might use this
        )
        # logger.debug("Reg 123-127 done")

    def update_metadata_postscan():
        # since we inherited ALL the user's namespace, we have RE and db
        scan_id = RE.md["scan_id"]
        uid = db[-1].start["uid"]
        yield from bps.mv(
            # source end values
            dm_pars.source_end_datetime, timestamp_now(),
            dm_pars.source_end_current, aps.current.value,
            dm_pars.uid, db[-1].start["uid"],
            dm_pars.scan_id, int(RE.md["scan_id"]),
            dm_pars.datafilename, areadet.plugin_file_name,
        )
        # logger.debug("dm_pars.datafilename")

    def inner_count(devices, md={}):
        yield from bps.open_run(md=md)
        for obj in devices:
            yield from bps.stage(obj)
        grp = bps._short_uid('trigger')
        no_wait = True
        for obj in devices:
            if hasattr(obj, 'trigger'):
                no_wait = False
                yield from bps.trigger(obj, group=grp)
        if areadet.cam.EXT_TRIGGER > 0:
            yield from soft_glue.start_trigger()
        # Skip 'wait' if none of the devices implemented a trigger method.
        if not no_wait:
            yield from bps.wait(group=grp)
        yield from bps.create('primary')
        # ret = {}  # collect and return readings to give plan access to them
        for obj in devices:
            reading = (yield from bps.read(obj))
            # if reading is not None:
            #     ret.update(reading)
        yield from bps.save()
        for obj in devices:
            yield from bps.unstage(obj)
        yield from bps.close_run()
        # return ret

    @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def full_acquire_procedure():
        logger.debug("before update_metadata_prescan()")
        yield from update_metadata_prescan()
        logger.debug("after update_metadata_prescan()")

        md = {
            "file_name": file_name,
            "file_path": file_path
        }
        # start autocount on the scaler
        yield from bps.mv(scaler1.count, "Count")
        logger.info("scaler should be autocounting now")

        # do the acquisition (the scan)
        logger.debug("before count()")
        # yield from bp.count([areadet], md=md)
        yield from inner_count([areadet], md=md)
        logger.debug("after count()")

        yield from update_metadata_postscan()
        hdf_with_fullpath = make_hdf5_workflow_filename()
        print(f"HDF5 workflow file name: {hdf_with_fullpath}")

        dm_workflow.create_hdf5_file(hdf_with_fullpath)
        
        # update these str values from the string registers
        dm_workflow.transfer = dm_pars.transfer.value
        dm_workflow.analysis = dm_pars.analysis.value

        # no need to yield from since the function is not a plan
        kickoff_DM_workflow(hdf_with_fullpath, analysis=submit_xpcs_job)

    @APS_utils.run_in_thread
    def kickoff_DM_workflow(hdf_workflow_file, analysis=True):
        logger.info(f"DM workflow kickoff starting: analysis:{analysis}  file:{hdf_workflow_file}")
        if analysis:
            out, err = dm_workflow.DataAnalysis(hdf_workflow_file)
        else:
            out, err = dm_workflow.DataTransfer(hdf_workflow_file)
        logger.info("DM workflow kickoff done")
        logger.info(out)
        if len(err) > 0:
            logger.error(err)

    logger.info("calling full_acquire_procedure()")
    return (yield from full_acquire_procedure())