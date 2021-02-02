
"""
ADRigaku UFXC area detector (EPICS)

* detector name: -tba-
* detector number: -tba-

see: https://github.com/aps-8id-dys/ipython-8idiuser/issues/251
"""

__all__ = ['adrigaku',]

from instrument.session_logs import logger
from ophyd import ADComponent as ADCpt
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase

logger.info(__file__)


IOC_PREFIX = "8idRigaku:"


class RigakuUfxcDetectorCam(CamBase):
    """
    Customization for the additional fields of the ADRigaku detector.

    see: https://github.com/BCDA-APS/ADRigaku
    """
    acquisition_delay = ADCpt(EpicsSignalWithRBV, 'AcquisitionDelay')
    calibration_label = ADCpt(EpicsSignalWithRBV, 'CalibrationLabel', string=True)
    exposure_delay = ADCpt(EpicsSignalWithRBV, 'ExposureDelay')
    file_name = ADCpt(EpicsSignalWithRBV, 'FileName', string=True)
    file_path = ADCpt(EpicsSignalWithRBV, 'FilePath', string=True)
    lower_threshold = ADCpt(EpicsSignalWithRBV, 'LowerThreshold')
    upper_threshold = ADCpt(EpicsSignalWithRBV, 'UpperThreshold')


class RigakuUfxcDetector(DetectorBase):
    _html_docs = ['RigakuUfxcDoc.html']
    cam = ADCpt(RigakuUfxcDetectorCam, 'cam1:')
    # TODO: other plugins: Sparse0, IMM


adrigaku = RigakuUfxcDetector(IOC_PREFIX, name="adrigaku")
