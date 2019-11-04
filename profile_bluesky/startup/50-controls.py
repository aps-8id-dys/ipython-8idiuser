logger.info(__file__)

"""local, custom Bluesky plans (scans)"""

from collections import namedtuple

# access by subscript or by name (obj[0]= same as obj.in)
in_out_tuple = namedtuple('in_out_tuple', 'in out')

class Presets:
    """
    various instrument settings and constants
    """
    pind1z = in_out_tuple(1, 0)  # TODO: what values?
    pind2z = in_out_tuple(1, 0)  # TODO: what values?
    pvFLUX_PIND = in_out_tuple(1, 0)

preset = Presets()

# Bluesky plans to move the diodes in/out

def pind1z_in():
    yield from bps.mv(pind1z, presets.pind1z.in)

def pind1z_out():
    yield from bps.mv(pind1z, presets.pind1z.out)

def pind2z_in():
    yield from bps.mv(pind2z, presets.pind2z.in)

def pind2z_out():
    yield from bps.mv(pind2z, presets.pind2z.out)

def pvFLUX_PIND_in():
    yield from bps.mv(pvFLUX_PIND, presets.pvFLUX_PIND.in)

def pvFLUX_PIND_out():
    yield from bps.mv(pvFLUX_PIND, presets.pvFLUX_PIND.out)

def move_diodes_in():
    "move ALL the diodes in"
    yield from bps.mv(
        pind1z, presets.pind1z.in,
        pind2z, presets.pind2z.in,
        pvFLUX_PIND, presets.pvFLUX_PIND.in,
    )

def move_diodes_out():
    "move ALL the diodes out"
    yield from bps.mv(
        pind1z, presets.pind1z.out,
        pind2z, presets.pind2z.out,
        pvFLUX_PIND, presets.pvFLUX_PIND.out,
    )


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

        RE(lineup_and_center("diode", ta2fine, -30, 30, 30, 1.0))
    """
    from ophyd import Kind

    old_sigs = scaler.stage_sigs
    scaler.stage_sigs["preset_time"] = time_s
    # yield from bps.mv(scaler.preset_time, time_s)

    scaler.select_channels([channel.name])
    clock.kind = Kind.normal

    md = _md.update
    md["purpose"] = "alignment"
    yield from bp.rel_scan([scaler], motor, minus, plus, npts, md=md)
    logger.info(f"tuned detector {channel.name} using motor {motor.name}:")
    for key in ('com', 'cen', 'max', 'min', 'fwhm', 'nlls'):
        logger.info(f"{key} = {bec.peaks[key][channel.name]}")

    yield from bps.mv(motor, bec.peaks["cen"][channel.name])

    # check if the position is ok
    # TODO: tweak ta2fine 2 to maximize

    scaler.select_channels(None)
    scaler.stage_sigs = old_sigs
