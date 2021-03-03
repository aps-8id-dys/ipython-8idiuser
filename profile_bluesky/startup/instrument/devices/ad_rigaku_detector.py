"""
ADRigaku UFXC area detector (EPICS)

* detector name: -tba-
* detector number: -tba-

see: https://github.com/aps-8id-dys/ipython-8idiuser/issues/251
"""

__all__ = [
    "adrigaku",
]

from instrument.session_logs import logger
from ophyd import ADComponent as ADCpt
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import Signal
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase

logger.info(__file__)


IOC_PREFIX = "8idRigaku:"


class RigakuUfxcDetectorCam(CamBase):
    """
    Customization for the additional fields of the ADRigaku detector.

    see: https://github.com/BCDA-APS/ADRigaku
    """

    acquisition_delay = ADCpt(EpicsSignalWithRBV, "AcquisitionDelay", kind="config")
    calibration_label = ADCpt(EpicsSignalWithRBV, "CalibrationLabel", string=True, kind="config")
    exposure_delay = ADCpt(EpicsSignalWithRBV, "ExposureDelay", kind="config")
    file_name = ADCpt(EpicsSignalWithRBV, "FileName", string=True, kind="config")
    file_path = ADCpt(EpicsSignalWithRBV, "FilePath", string=True, kind="config")
    lower_threshold = ADCpt(EpicsSignalWithRBV, "LowerThreshold", kind="config")
    upper_threshold = ADCpt(EpicsSignalWithRBV, "UpperThreshold", kind="config")

    corrections = ADCpt(EpicsSignal, "Corrections", kind="config", string=True)  # has no _RBV PV

    # remove these attributes from CamBase
    pool_max_buffers = None


class RigakuUfxcDetector(DetectorBase):
    _html_docs = ["RigakuUfxcDoc.html"]
    cam = ADCpt(RigakuUfxcDetectorCam, "cam1:")
    # TODO: other plugins: Sparse0, IMM

    staging_mode = ADCpt(Signal, value="fast", kind="config")

    def staging_setup_DM(self, *args, mode=None):

        """
        setup the detector's stage_sigs for acquisition with the DM workflow
        from DM_DeviceMixinAreaDetector
        """

        # If staging stalls, it is because one or more of the signals
        # is being set by its string value instead of the enumeration
        # number.  This happens with EpicsSignalWithRBV when it was 
        # called without the string=True kwarg.
        #     In [13]: adrigaku.cam.image_mode.get()
        #     Out[13]: 9

        #     In [14]: adrigaku.cam.image_mode.get(as_string=True)
        #     Out[14]: '16 Bit, 1S'
        # The fix is to set by number, not string.
        if (mode == 'fast'):
            self.stage_sigs = {}
            self.stage_sigs["cam.acquire_time"] = 20e-6
            self.stage_sigs["cam.image_mode"] = 5
            self.stage_sigs["cam.trigger_mode"] = 4
            self.stage_sigs["cam.num_images"] = 100_000   # "_" is a visual separator
            self.stage_sigs["cam.corrections"] = "Enabled"
            self.stage_sigs["cam.data_type"] = "UInt32"
            # TODO: what else is needed?

        elif (mode == 'slow'):            self.stage_sigs = {}
            self.stage_sigs["cam.image_mode"] = 9  # "16 Bit, 1S"
            self.stage_sigs["cam.trigger_mode"] = 0  # "Fixed Time"
            self.stage_sigs["cam.acquire_time"] = 0.1
            self.stage_sigs["cam.num_images"] = 10
            self.stage_sigs["cam.data_type"] = "UInt16"
            self.stage_sigs["cam.corrections"] = "Disabled"
            # TODO: what else is needed?

            # TODO: Need the equivalent of the lines below:

            # epics_put("8idRigaku:IMM1:AutoIncrement", "Yes")
            # epics_put("8idRigaku:IMM1:NumCapture",10) 
            # epics_put("8idRigaku:IMM1:FileNumber",1)
            # epics_put("8idRigaku:IMM1:FilePath","/Rigaku/bin/destination/RigakuEpics/");
            # epics_put("8idRigaku:IMM1:FileName","test");            

        self.batch_name.put(self._file_name)


adrigaku = RigakuUfxcDetector(IOC_PREFIX, name="adrigaku")
