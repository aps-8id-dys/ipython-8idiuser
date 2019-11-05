logger.info(__file__)

"""
local, custom Bluesky plans (scans)

Classes and Other Structures

    insert_remove_tuple
    Presets

Variables

    presets

Plans

    bb
    beam_params_backup
    beam_params_restore
    insert_diodes
    insert_flux_pind
    insert_pind1
    insert_pind2
    lineup_and_center
    remove_diodes
    remove_flux_pind
    remove_pind1_out
    remove_pind2
    sb
    tw (not implemented yet)

Functions

    calc_flux
    flux
    flux_params
    print_flux_params
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

def remove_pind1_out():
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
    old_sigs = scaler.stage_sigs
    old_position = motor.position
    scaler.stage_sigs["preset_time"] = time_s
    # yield from bps.mv(scaler.preset_time, time_s)

    scaler.select_channels([counter.name])
    clock.kind = Kind.normal

    aligned = False

    def peak_analysis():
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

            if hi < peak_factor*lo:
                logger.error(f"no clear peak: {hi} < {peak_factor}*{lo}")
                final = old_position
            elif fwhm > width_factor*x_range:
                logger.error(f"FWHM too large: {fwhm} > {width_factor}*{x_range}")
                final = old_position

            logger.info(f"moving {motor.name} to {final}")
            yield from bps.mv(motor, final)
            aligned = True
        else:
            logger.error("no statistical analysis of scan peak!")
            yield from bps.null()

    md = dict(_md)
    md["purpose"] = "alignment"
    yield from bp.rel_scan([scaler], motor, minus, plus, npts, md=md)
    yield from peak_analysis()

    if aligned:
        # again, tweak axis to maximize
        md["purpose"] = "alignment - fine"
        fwhm = bec.peaks["fwhm"][counter.name]
        lo = max(old_position+minus, -fwhm/2)
        hi = min(old_position+plus, fwhm/2)
        yield from bp.scan([scaler], motor, lo, hi, npts, md=md)
        width_factor = 1
        yield from peak_analysis()

    scaler.select_channels(None)
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


def sb():
    """show beam"""
    yield from bps.mv(shutter, "open")


def tw(counter, motor, delta):
    """
    maximize a positioner using a motor and reading a scaler channel

    In SPEC, the `tw` command initiates an interactive session.
    Automate that here, if possible.
    """
    # Usage:  tw mot [mot2 ...] delta [delta2 ...] [count_time]
    raise NotImplementedError("Need to write the Bluesky tw() plan")

# -----------------------------------------------------------------------

PV_REG_MAP = {
    "template": "8idi:Reg%d",
    "detector_pv" : "8idi:Reg2",
    "registers/detector": 10,
    "highest register": 170,
    "regpv_start": {
        "current" : 10,
        "LAMBDA" : 90,
        "RIGAKU1" : 140,
    },
    "detectors" : {
        25 : "LAMBDA",
        46 : "RIGAKU1",
    }
}
PV_REG_MAP["registers"] = [     # each register is a signal
    EpicsSignal(
        PV_REG_MAP["template"] % (i+1), 
        name="pv_reg%d" % (i+1)
        )
    for i in range(PV_REG_MAP["highest register"])
    ]
PV_REG_MAP["registers"].insert(0, None)     # offset since no 8idi:Reg0


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
    logger.debug(f"Detector {detName} Beam Params are restored\n{t}")


def select_LAMBDA(*args, **kwargs):
    """
def select_LAMBDA '
    	beam_params_backup;
	epics_put(DETECTOR_REGISTER_PV, LAMBDA_detector_num)
	epics_put("8idi:Reg5",3930.00); ##moved sample 7 inches closer to detector
	##epics_put("8idi:Reg5",7800.00); ##moved sample 7 inches closer to detector
	epics_put("8idi:Reg4",240.00);
	beam_params_restore;
    
    	blockbeam;

	printf("Moving LAMBDA PAD to the direct beam position\n");
	getangles;
    #####2 lines below for 4 m distance
    A[ccdx]=epics_get(ccdx0_pv);A[ccdz]=epics_get(ccdz0_pv);move_em;uwm ccdx ccdz;
	A[ccdx]= 214.10;A[ccdz]= 36.95;move_em; uwm ccdx ccdz
    
    #####2 lines below for 8 m distance
    #A[dsccdx]=epics_get(ccdx0_pv);A[dsccdz]=epics_get(ccdz0_pv);move_em;uwm dsccdx dsccdz;
	#A[dsccdx]= 127.53;A[dsccdz]= 15.55;move_em; uwm dsccdx dsccdz
	shutteroff;
	use_blockbeam_Lambda

        ccdhook_ad_nofpga_Lambda 8LAMBDA1:cam1: 8LAMBDA1:IMMout: 8LAMBDA1:cam1:  8LAMBDA1:Stats1: 8LAMBDA1:Proc1:
        
        #setccdc_ad 0  #set CCD_MONITOR_ROI
        
	DIR_SLASH="/"

	LAMBDA_data_path

        CCD_FILE_EXT="imm"
	ccdsetup  
	sleep(1.0);
	##Lambda_Set_EnergyThreshold 5.5;

        use_blockbeam_Lambda 
	##def shutteron \' shutteron_default \';
	##def shutteroff \' shutteroff_default \';
        ##shutteron;
	
	epics_put("8idi:softGlueB:BUFFER-1_IN_Signal",1); #sends  external pulse train signal to the trigger
	###epics_put("8idi:softGlueC:MUX2-1_SEL_Signal",0); #sets shutter signal pulse train to single(0)/burst(1) mode
	###epics_put("8idi:softGlueC:MUX2-2_SEL_Signal",0); #sends detector signal pulse train to burst mode
	###ccdtype_shutter_control_select 1
        
	shutteroff_default;
	def shutteron \'  \';
	def shutteroff \'  \';
	
#	umv si2hgap 20;umv si2vgap 20;

	def xpcs_pre_start \'xpcs_pre_start_LAMBDA\';
	def user_xpcs_loop \'user_xpcs_loop_LAMBDA\';

	UFXC_align_mode

        epics_put(BURST_MODE_REGISTER_PV, 0); ##setting burst mode default status (May 2019 onwards)
	DM_WORKFLOW_DATA_TRANSFER = "xpcs8-01-Lambda"
	DM_WORKFLOW_DATA_ANALYSIS = "xpcs8-02-Lambda"
    epics_put("8idi:StrReg15", DM_WORKFLOW_DATA_TRANSFER)
    epics_put("8idi:StrReg16", DM_WORKFLOW_DATA_ANALYSIS)
'
    """
