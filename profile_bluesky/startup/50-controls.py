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

    bb
    beam_params_backup
    beam_params_restore
    blockbeam
    block_directbeam_common
    insert_diodes
    insert_flux_pind
    insert_pind1
    insert_pind2
    lineup_and_center
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

def lineup_and_center(counter, motor, minus, plus, npts, time_s=0.1, peak_factor=4, width_factor=0.8,_md={}):
    """
    lineup and center a given axis, relative to current position

    PARAMETERS
    
    counter : scaler channel object
        detector to be maximized
    
    axis : motor
        motor to use for alignment
    
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

        RE(lineup_and_center("diode", foemirror.theta, -30, 30, 30, 1.0))
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

    if hasattr(motor, "position"):
        old_position = motor.position
    else:
        old_position = motor.value

    def peak_analysis():
        aligned = False
        if counter.name in bec.peaks["cen"]:
            table = pyRestTable.Table()
            table.labels = ("key", "value")
            table.addRow(("motor", motor.name))
            table.addRow(("detector", counter.name))
            table.addRow(("starting position", old_position))
            for key in bec.peaks.ATTRS:
                table.addRow((key, bec.peaks[key][counter.name]))
            logger.info(f"alignment scan results:\n{table}")

            lo = bec.peaks["min"][counter.name][-1]  # [-1] means detector
            hi = bec.peaks["max"][counter.name][-1]  # [0] means motor
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
            
            logger.info(f"moving {motor.name} to {final}  (aligned: {aligned})")
            yield from bps.mv(motor, final)
        else:
            logger.error("no statistical analysis of scan peak!")
            yield from bps.null()

        # too sneaky?  We're modifying this structure locally
        bec.peaks.aligned = aligned
        bec.peaks.ATTRS =  ('com', 'cen', 'max', 'min', 'fwhm')

    md = dict(_md)
    md["purpose"] = "alignment"
    yield from bp.rel_scan([counter], motor, minus, plus, npts, md=md)
    yield from peak_analysis()

    if bec.peaks.aligned:
        # again, tweak axis to maximize
        md["purpose"] = "alignment - fine"
        fwhm = bec.peaks["fwhm"][counter.name]
        yield from bp.rel_scan([counter], motor, -fwhm, fwhm, npts, md=md)
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
        t.addRow((source.value, source.pvname, target.pvname))
        yield from bps.mv(target, source.value)
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
        t.addRow((source.value, source.pvname, target.pvname))
        yield from bps.mv(target, source.value)
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


nextpos = 0
samxdata = np.linspace(0, 2, 21)    # example: user will change this
samzdata = np.linspace(0, .5, 15)    # example: user will change this


def movesample():
    global nextpos
    global samxdata
    global samzdata
    if dm_pars.geometry_num.value == 0: # transmission
        xn = len(samxdata)
        zn = len(samzdata)
        if xn > zn:
            x = nextpos % xn
            z = int(nextpos/xn) % zn
        else:
            x = int(nextpos/zn) % xn
            z = nextpos % zn
    else:    # reflection
        x = nextpos % len(samxdata)
        z = nextpos % len(samzdata)

    x = samxdata[x]
    z = samzdata[z]
    logger.info(f"Moving samx to {x}, samz to {z}")
    yield from bps.mv(
        samplestage.x, x,
        samplestage.z, z,
        )
    nextpos += 1


def movesamx():
    global nextpos
    global samxdata
    index = nextpos % len(samxdata)
    p = samxdata[index]
    logger.info(f"Moving samx to {p}")
    yield from bps.mv(samplestage.x, p)
    nextpos += 1


def movesamz():
    global nextpos
    global samzdata
    index = nextpos % len(samzdata)
    p = samzdata[index]
    logger.info(f"Moving samz to {p}")
    yield from bps.mv(samplestage.z, p)
    nextpos += 1


# --------------------------------------------------------------------

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
