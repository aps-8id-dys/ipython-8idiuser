
"""
QZ's collection
"""

__all__ = [
    'align_x',
    'align_z',
]

from instrument.session_logs import logger
logger.info(__file__)

from instrument.devices import pind4, lakeshore, samplestage
from instrument.plans import sb, bb
from instrument.startup import bp, bps

logger.warning("Call pre_align() with shutter OPEN before you run RE(align_x())")


def align_x(pos_start=-3,
            pos_stop=-3,
            num_pts=61):  
    yield from sb() 
    yield from bp.rel_scan([pind4,lakeshore],samplestage.x,pos_start,pos_stop,num_pts) 
    yield from bb()
                                                                                                                                                     

def align_z(pos_start=-2,
            pos_stop=-2,
            num_pts=41):  
    yield from sb() 
    yield from bp.rel_scan([pind4,lakeshore],samplestage.z,pos_start,pos_stop,num_pts) 
    yield from bb() 
