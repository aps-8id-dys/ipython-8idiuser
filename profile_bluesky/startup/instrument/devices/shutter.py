
"""
shutter support
"""

__all__ = [
    'shutter',
    'shutter_control',
    'shutter_mode',
    'shutter_override',
]

from instrument.session_logs import logger
logger.info(__file__)

from apstools.devices import EpicsOnOffShutter
from apstools.devices import SimulatedApsPssShutterWithStatus
from bluesky.suspenders import SuspendFloor
from instrument.devices import aps
from instrument.devices import operations_in_8idi
from instrument.startup import RE, sd
from ophyd import EpicsSignal


if aps.inUserOperations and operations_in_8idi():
    sd.monitors.append(aps.current)

    # suspend when current < 2 mA
    # resume 100s after current > 10 mA
    logger.info("Installing suspender for low APS current.")
    suspend_APS_current = SuspendFloor(aps.current, 2, resume_thresh=10, sleep=100)
    RE.install_suspender(suspend_APS_current)

    shutter = EpicsOnOffShutter("8idi:Unidig1Bo13", name="shutter")
    shutter.close_value = 1
    shutter.open_value = 0

else:
    logger.warning("!"*30)
    if operations_in_8idi():
        logger.warning("Session started when APS not operating.")
    else:
        logger.warning("Session started when 8_ID-I is not operating.")
    logger.warning("Using simulator 'shutter'.")
    logger.warning("!"*30)
    # simulate a shutter (no hardware required)
    shutter = SimulatedApsPssShutterWithStatus(name="shutter", labels=["shutter", "simulator"])
    shutter.delay_s = 0.05 # shutter needs short recovery time after moving


shutter_control = EpicsSignal("8idi:Unidig1Bo13", name="shutter_control")

# values: "UFXC" : acquire mode, "1UFXC" : align mode
shutter_mode = EpicsSignal("8idi:softGlueC:AND-4_IN2_Signal", name="shutter_mode")

shutter_override = EpicsSignal("8idi:Unidig1Bo9.VAL", name="shutter_override")
