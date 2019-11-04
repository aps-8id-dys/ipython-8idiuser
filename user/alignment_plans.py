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

    yield from lineup_and_center(channel, motor, -30, 30, 30, 1.0, md=md)

    # prints the flux
    flux(pind1, channel.value)     # TODO: channel.value?
    ##flux should be 1.0-1.6 E12 ph/sec

    yield from bp.mv(si1.x, 0.2)
    yield from bp.mvr(diamond.x, 1.0)     # NOTE: *relative* move here
    yield from bp.mv(
        si1.hcen, 50,
        si1.hgap, 60,
        si1.vgap, 150,
    )
