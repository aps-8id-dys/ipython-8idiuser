
import apstools.synApps
from ophyd import EpicsSignalRO
from ..session_logs import logger
logger.info(__file__)

__all__ = ['calcs', 'calcouts']

calcs = apstools.synApps.UserCalcsDevice("sky:", name="calcs")
calcouts = apstools.synApps.UserCalcoutDevice("sky:", name="calcouts")

calcs.enable.put(1)
