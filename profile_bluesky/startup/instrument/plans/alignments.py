
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
from ..devices import shutter, shutter_mode, scaler1
from .shutters import sb, bb


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
        motor_name,
        pos_start,
        pos_stop,
        num_pts,
        count_time):
        
    yield from sb() 
    scaler1.stage_sigs["preset_time"] = count_time
    scaler1.stage_sigs["count_mode"] = "OneShot"
    scaler1.stage_sigs["auto_count_delay"] = 1
    scaler1.select_channels([channel.name])
    yield from bp.rel_scan(
        [scaler1, lakeshore],
        motor_name,
        pos_start,
        pos_stop,
        num_pts,
        ) 
    scaler1.select_channels(None)    # selects all named channels again
    del scaler1.stage_sigs["preset_time"]
    del scaler1.stage_sigs["count_mode"]
    del scaler1.stage_sigs["auto_count_delay"]
    yield from bb()

