
"""
Command-line functions for alignment - NOT bluesky plans
"""

__all__ = [
    "pre_align",
    "post_align",
]

from instrument.session_logs import logger
logger.info(__file__)

from ..devices import actuator_flux, att, default_counter, pind4
from ..devices import shutter, shutter_mode

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
