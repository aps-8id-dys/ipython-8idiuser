


"""
Acquire an XPCS measurement with a supported area detector
"""

__all__ = """
    AD_Acquire
""".split()

from instrument.session_logs import logger
logger.info(__file__)

from ..devices import aps, detu, I0Mon, soft_glue
from ..devices import aps, dm_pars, dm_workflow
from ..devices import Atten1, Atten2, scaler1
from ..devices import timebase, pind1, pind2, T_A, T_SET
from ..framework import db, RE
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
import apstools.utils
import datetime
import ophyd.signal
import os


def Detector_Acq(areadet,             
                trigger_mode,
               file_name,
               acquire_time,
               acquire_period,
               num_images,
               path=None,
               md={}):
    
    """
    Acquires xpcs data with area detector.

    Can specify different trigger mode based on the class of detector and the trigger mode it supports.

    1. Configure the detectors for staging (need to modify the detector classes);
        The file plugin will be determined based on the extension of the file name
    2. Stage the detector (populate the EPICS IOC with acquisition parameters);
    3. Trigger the detector (e.g. use Start button for internal mode and send trigger pulse for external mode)
    4. Wait for acquisition to finish.

    """

    areadet.preconfigure(trigger_mode, file_name, acquire_time, acquire_period, num_images, path)

    yield from bps.stage(areadet)  # Step 2

    yield from bps.trigger(areadet, group="areadet")  # Step 3

    yield from bps.wait("areadet", )  # Step 4

    def preconfigure(self,
                trigger_mode,
               file_name,
               acquire_time,
               acquire_period,
               num_images,
               path=None):   # Each detector needs this method. Copy into the detector classes.
        """
        Setup staging, trigger mode
        """
    