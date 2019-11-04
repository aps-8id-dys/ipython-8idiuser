logger.info(__file__)

"""local, custom Bluesky plans (scans)"""


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

def lineup_and_center(channel, motor, minus, plus, npts, time_s=0.1, _md={}):
    """
    lineup and center a given axis, relative to current position

    PARAMETERS
    
    channel : scaler channel object
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

    EXAMPLE:

        RE(lineup_and_center("diode", foemirror.theta, -30, 30, 30, 1.0))
    """
    old_sigs = scaler.stage_sigs
    old_position = motor.position
    scaler.stage_sigs["preset_time"] = time_s
    # yield from bps.mv(scaler.preset_time, time_s)

    scaler.select_channels([channel.name])
    clock.kind = Kind.normal

    md = dict(_md)
    md["purpose"] = "alignment"
    yield from bp.rel_scan([scaler], motor, minus, plus, npts, md=md)

    if channel.name in bec.peaks["cen"]:
        table = pyRestTable.Table()
        table.labels = ("key", "value")
        table.addRow(("motor", motor.name))
        table.addRow(("detector", channel.name))
        for key in ('com', 'cen', 'max', 'min', 'fwhm', 'nlls'):
            table.addRow((key, bec.peaks[key][channel.name]))
        logger.info("alignment scan results:")
        logger.info(str(table))

        # TODO: min & max are for diode or motor?
        # lo = bec.peaks["min"][channel.name]
        # hi = bec.peaks["max"][channel.name]
        fwhm = bec.peaks["fwhm"][channel.name]
        final = bec.peaks["cen"][channel.name]
        # if centroid < lo:
        #     logger.error(f"centroid too low: {final} < {lo}")
        #     final = old_position
        # elif centroid > hi:
        #     logger.error(f"centroid too high: {final} > {hi}")
        #     final = old_position

        # move motor to final position
        logger.info(f"moving {motor.name} to {final}")
        yield from bp.mv(motor, final)
    else:
        logger.error("no statistical analysis of scan peak!")

    # TODO:tweak foemirror.theta to maximize
    # md["purpose"] = "alignment - fine"
    # lo = max(lo, fwhm/2)
    # hi = min(hi, fwhm/2)
    # yield from bp.rel_scan([scaler], motor, lo, hi, npts, md=md)

    scaler.select_channels(None)
    scaler.stage_sigs = old_sigs


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


def bb(*args, **kwargs):
    """
    block beam

    bb -> blockbeam -> blockbeam_Lambda

    # /home/beams/8IDIUSER/batches/2019/Oct2019/Lambda_rubber_both4X.do
    def blockbeam 'blockbeam_Lambda'

    745.SPEC8IDI> prdef blockbeam_Lambda

    # /home/beams/8IDIUSER/local_macros/CCD_macros/xpcs_ad_nofpga_Lambda_AD3p0_EXTTRIG.mac
    def blockbeam_Lambda '
        ##epics_put("8idi:BioEnc2B1.VAL","Down");
        ##epics_put("8idi:BioEnc2B3.VAL","Close");
        epics_put("8idi:Unidig1Bo13","Closed");
    '

    """
    yield from bp.mv(shutter, "close")


def sb(*args, **kwargs):
    """show beam"""
    yield from bp.mv(shutter, "open")


def tw(channel, motor, delta):
    """
    maximize a positioner using a motor and reading a scaler channel

    In SPEC, the `tw` command initiates an interactive session.
    Automate that here, if possible.
    """
    # Usage:  tw mot [mot2 ...] delta [delta2 ...] [count_time]
    raise NotImplementedError("Need to write the Bluesky tw() plan")


def calc_flux(cps, params, pin_diode):
    """
    """
    gain = preamps.gains[pin_diode.name]
    amps = (cps/params["CtpV"])*gain
    photons = amps/(1.60218e-19*params["N_elec"]*params["Abs_frac"])
    return photons

