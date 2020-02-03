# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)


"""
bluesky data acquisition plans

Load this file with the command:

    %run -m alignment_plans
"""

def Rinaldi_group_alignment(_md={}):
    """
    bluesky plan to align (for Rinaldi group, 2019-10)
    """
    md = dict(_md)

    channel = pind1     # the EpicsSignalRO (scaler channel) object, not the string name
    motor = ta2fine     # the EpicsMotor object, not the string name
    yield from insert_pind1()

    yield from bp.mv(si1.x, 0.0)
    yield from bp.mvr(diamond.x, -1)     # NOTE: *relative* move here
    yield from bp.mv(
        si1.hcen, 0,
        si1.hgap, 250,
        si1.vgap, 250,
    )

    yield from lineup(channel, motor, -30, 30, 30, 1.0, md=md)

    # prints the flux, scaled to 100 mA APS current
    count_rate = channel.get() / timebase.get() * 1e6 * aps.current.get() / 100
    v = flux(pind1, count_rate)
    if v < 1e12:
        logger.warning(f"computed flux {v} is low, expected at least 1e12")
    elif v > 1.6e12:
        logger.warning(f"computed flux {v} is high, expected at most 1.6e12")


    yield from bp.mv(si1.x, 0.2)
    yield from bp.mvr(diamond.x, 1.0)     # NOTE: *relative* move here
    yield from bp.mv(
        si1.hcen, 50,
        si1.hgap, 60,
        si1.vgap, 150,
    )
