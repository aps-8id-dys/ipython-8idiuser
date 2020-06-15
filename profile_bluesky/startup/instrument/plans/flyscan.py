
"""
Bluesky plans for fly scan
"""

__all__ = [
    "flyscan_spinner",
]

from instrument.session_logs import logger
logger.info(__file__)

from ..devices import flyscan
from bluesky import plan_stubs as bps



# flyscan_setup FLY_START_POS FLY_START_POS+2.5*FLY_SPEED FLY_SPEED   ##start,end,speed in mm/sec
def flyscan_spinner(start_pos, end_pos, fly_speed):
    yield from flyscan.setup(start_pos, end_pos, fly_speed)
    yield from bps.abs_set(flyscan, "taxi", wait=True)
    yield from bps.abs_set(flyscan, "fly", wait=False)
