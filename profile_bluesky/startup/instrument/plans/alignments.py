
"""
Command-line functions for alignment - NOT bluesky plans
"""

__all__ = [
    "pre_align",
    "post_align",
    "align_x",
    "align_z",
    "lup",
]


from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plans as bp
from bluesky import plan_stubs as bps

from ..devices import actuator_flux, att, default_counter, pind4, lakeshore, samplestage
from ..devices import scaler1
# from ..devices import shutter, shutter_override
# from .shutters import sb, bb


def pre_align():
    """
    This is not a plan and so we should use it in command line, which means no use of RE
    """
    global att, default_counter
    shutter.close()
    actuator_flux.put("IN")
    att.put(2)
    default_counter = pind4
    shutter_override.put(0)

def post_align():
    """
    This is not a plan and so we should use it in command line, which means no use of RE
    """
    global att
    shutter.close()
    actuator_flux.put("OUT")
    att.put(0) #att will be defined to att1 or att2


# QZ added on 2020/05/28


def align_x(pos_start=-0.5,
            pos_stop=0.5,
            num_pts=41):
    yield from sb()
    yield from bp.rel_scan([pind4,lakeshore],samplestage.x,pos_start,pos_stop,num_pts)
    yield from bb()


def align_z(pos_start=-0.5,
            pos_stop=0.5,
            num_pts=41):
    yield from sb()
    yield from bp.rel_scan([pind4,lakeshore],samplestage.z,pos_start,pos_stop,num_pts)
    yield from bb()


def lup(channel,
        motor,
        pos_start,
        pos_stop,
        num_pts,
        count_time,
        md=None):

    
    _md = {}
    _md["plan_name"] = "lup"
    _md["channel_name"] = channel.name
    _md["motor_name"] = motor.name
    _md["num_pts"] = num_pts
    _md["pos_start"] = pos_start
    _md["pos_stop"] = pos_stop
    _md.update(md or {})

    yield from sb()
    original_stage_sigs = dict(scaler1.stage_sigs)
    scaler1.stage_sigs["preset_time"] = count_time
    scaler1.stage_sigs["count_mode"] = "OneShot"
    scaler1.stage_sigs["auto_count_delay"] = 1
    scaler1.select_channels([channel.name])
    yield from bp.rel_scan(
        [scaler1, lakeshore],
        motor,
        pos_start,
        pos_stop,
        num_pts,
        md=_md
        )
    scaler1.select_channels(None)    # selects all named channels again
    scaler1.stage_sigs = dict(original_stage_sigs)
    yield from bb()

