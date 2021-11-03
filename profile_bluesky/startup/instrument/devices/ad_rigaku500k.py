"""
Rigaku500k definition by QZ
"""

__all__ = [
    "rigaku500k",
]

from .ad_acquire_detector_base import AD_AcquireDetectorBase
from .ad_acquire_detector_base import AD_AcquireDetectorCamBase
from .ad_imm_plugins import IMM_DeviceMixinBase
from .data_management import DM_DeviceMixinAreaDetector
from bluesky import plan_stubs as bps
from instrument.session_logs import logger
from ophyd import ADComponent as ADCpt
from ophyd import ADTriggerStatus
from ophyd import EpicsSignal
# from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import Signal
from ophyd import SingleTrigger
from ophyd import Staged
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
import os
import time as ttime

logger.info(__file__)


IOC_PREFIX = "8idRigaku:"


class Rigaku500kCam(CamBase):

    acquisition_delay = ADCpt(EpicsSignalWithRBV, "AcquisitionDelay", kind="config")
    calibration_label = ADCpt(EpicsSignalWithRBV, "CalibrationLabel", string=True, kind="config")
    exposure_delay = ADCpt(EpicsSignalWithRBV, "ExposureDelay", kind="config")
    file_name = ADCpt(EpicsSignalWithRBV, "FileName", string=True, kind="config")
    file_path = ADCpt(EpicsSignalWithRBV, "FilePath", string=True, kind="config")
    lower_threshold = ADCpt(EpicsSignalWithRBV, "LowerThreshold", kind="config")
    upper_threshold = ADCpt(EpicsSignalWithRBV, "UpperThreshold", kind="config")

    corrections = ADCpt(
        EpicsSignal, "Corrections", kind="config", string=True
    )

    staging_mode = ADCpt(Signal, value="fast", kind="config")

    # remove these attributes from CamBase
    pool_max_buffers = None
    EXT_TRIGGER = 0

class Rigaku500k(
    SingleTrigger,
    DetectorBase,
):

    cam = ADCpt(Rigaku500kCam, "cam1:")
    _status_type = ADTriggerStatus


# wait a bit for all previous PV connections to complete
_delay = 2.5  # empirical determination (1.0 is too short, 2 tests OK)
logger.info("Sleeping for %s seconds before creating adrigaku object.", _delay)
ttime.sleep(_delay)

rigaku500k = Rigaku500k(IOC_PREFIX, name="rigaku500k")