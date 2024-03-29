
"""
shutter support
"""

__all__ = [
    'shutter',
    'shutter_control',
    'shutter_override',
    'shutterstage',
    'shutteroff',
    'shutteron',
]

from instrument.session_logs import logger
logger.info(__file__)

from apstools.devices import EpicsOnOffShutter
from apstools.devices import SimulatedApsPssShutterWithStatus
from bluesky.suspenders import SuspendFloor
from instrument.devices import aps
from instrument.devices import operations_in_8idi
from instrument.framework import RE, sd
from ophyd import Component, Device, EpicsMotor
from ophyd import EpicsSignal
import time

class MySimulatedFastShutter(SimulatedApsPssShutterWithStatus):
    
    def wait_for_state(self, target, timeout=10, poll_s=0.01):
        simulated_response_time_s = 0.05
        time.sleep(simulated_response_time_s)
        self.pss_state.put(target[0])


if aps.inUserOperations and operations_in_8idi():
    sd.monitors.append(aps.current)

    # # suspend when current < 2 mA
    # # resume 100s after current > 10 mA
    # logger.info("Installing suspender for low APS current.")
    # suspend_APS_current = SuspendFloor(aps.current, 2, resume_thresh=10, sleep=100)
    # RE.install_suspender(suspend_APS_current)

    # shutter = EpicsOnOffShutter("8idi:Unidig1Bo13", name="shutter")
    shutter = MySimulatedFastShutter(name="shutter")
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


class ShutterStage(Device):
    """
    Shutter Stage at 8-ID-I
    """
    x = Component(EpicsMotor, '8idi:m1', labels=["motor", "shutter"])
    z = Component(EpicsMotor, '8idi:m2', labels=["motor", "shutter"])


shutter_control = EpicsSignal("8idi:Unidig1Bo13", name="shutter_control")
shutter_override = EpicsSignal("8idi:Unidig1Bo9.VAL", name="shutter_override")
shutterstage = ShutterStage(name="shutterstage")


# these are for the shutter_override, but are NOT plans
# same as used in SPEC
def shutteroff():
    """Blocking function to allow shutter control with sb & bb"""
    shutter_override.put("High")


def shutteron():
    """Blocking function to prevent shutter control with sb & bb"""
    shutter_override.put("Low")
