
"""
EPID: Enhanced Proportional-Integral-Derivative controls
"""

__all__ = ['pid1', 'pid2']

from instrument.session_logs import logger
logger.info(__file__)

from apstools.synApps import EpidRecord

class ModifiedEpidRecord(EpidRecord):
    clock_ticks = None

pid1 = ModifiedEpidRecord("8idi:pid1", name="pid1", labels=["pid",])
pid2 = ModifiedEpidRecord("8idi:pid2", name="pid2", labels=["pid",])
