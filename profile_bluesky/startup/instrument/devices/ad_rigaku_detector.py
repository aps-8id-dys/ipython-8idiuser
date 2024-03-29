"""
ADRigaku UFXC area detector (EPICS)
* detector name: -tba-
* detector number: -tba-
see: https://github.com/aps-8id-dys/ipython-8idiuser/issues/251
"""

__all__ = [
    "adrigaku",
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


class RigakuUfxcDetectorCam(AD_AcquireDetectorCamBase, CamBase):
    """
    Customization for the additional fields of the ADRigaku detector.
    see: https://github.com/BCDA-APS/ADRigaku
    """

    acquisition_delay = ADCpt(EpicsSignalWithRBV, "AcquisitionDelay", kind="config")
    calibration_label = ADCpt(
        EpicsSignalWithRBV, "CalibrationLabel", string=True, kind="config"
    )
    exposure_delay = ADCpt(EpicsSignalWithRBV, "ExposureDelay", kind="config")
    file_name = ADCpt(EpicsSignalWithRBV, "FileName", string=True, kind="config")
    file_path = ADCpt(EpicsSignalWithRBV, "FilePath", string=True, kind="config")
    lower_threshold = ADCpt(EpicsSignalWithRBV, "LowerThreshold", kind="config")
    upper_threshold = ADCpt(EpicsSignalWithRBV, "UpperThreshold", kind="config")

    corrections = ADCpt(
        EpicsSignal, "Corrections", kind="config", string=True
    )  # has no _RBV PV

    staging_mode = ADCpt(Signal, value="fast", kind="config")

    # remove these attributes from CamBase
    pool_max_buffers = None
    EXT_TRIGGER = 0

    def setTime(self, exposure_time, exposure_period):
        """
        Set exposure time and period.
        """
        yield from bps.mv(self.acquire_time, exposure_time)
        yield from bps.mv(self.acquire_period, exposure_period)


class RigakuUfxcDetector(
    AD_AcquireDetectorBase,
    DM_DeviceMixinAreaDetector,
    # IMM_DeviceMixinBase,
    SingleTrigger,
    DetectorBase,
):
    _html_docs = ["RigakuUfxcDoc.html"]
    cam = ADCpt(RigakuUfxcDetectorCam, "cam1:")
    # TODO: other plugins: Sparse0
    qmap_file = "Rigaku_Sample_Rq0.h5"
    detector_number = 46  # 8-ID-I numbering of this detector
    _status_type = ADTriggerStatus


    def setup_modes(self, num_triggers):

        # yield from bps.mv(self.cam.staging_mode, mode)  # at least must yield *some* bluesky message
        yield from bps.null()


    def staging_setup_DM(self, *args, **kwargs):

        """
        setup the detector's stage_sigs for acquisition with the DM workflow
        from DM_DeviceMixinAreaDetector
        """
        self._file_name = args[1]
        logger.info("Rigaku file name, %s", self._file_name)

        # template from previous support
        # areadet.staging_setup_DM(file_path, file_name,
        #         num_images, acquire_time, acquire_period)
        # root = os.path.join("/", "home", "8-id-i-stage/")
        # folder = self._file_name
        # fname = (
        #     f"{folder}"
        #     f"_{dm_pars.data_begin.get():05.0f}"
        #     f"-{dm_pars.data_end.get():05.0f}"
        #     ".bin"
        # )
        file_path = args[0]
        # Rigaku has our "/home/8ididata" mounted as "/Rigaku/bin/destination"
        # Our bin file starts relative to that mount.
        fpath = file_path.replace("/home/8ididata/", "")
        fname = f"{fpath}{self._file_name}"

        # makedir(UFXC_fullpath_datafolder);
        # unix(sprintf("chmod 777 %s", UFXC_fullpath_datafolder))
        print("DEBUG: file_path (bluesky): ", file_path)
        print("DEBUG: file_path (detector): ", fpath)
        os.makedirs(file_path, mode=0o777,exist_ok=True)

        # If staging stalls, it is because one or more of the signals
        # is being set by its string value instead of the enumeration
        # number.  This happens with EpicsSignalWithRBV when it was
        # called without the string=True kwarg.
        #     In [13]: adrigaku.cam.image_mode.get()
        #     Out[13]: 9

        #     In [14]: adrigaku.cam.image_mode.get(as_string=True)
        #     Out[14]: '16 Bit, 1S'
        # The fix is to set by number, not string.

        self.stage_sigs["cam.file_path"] = os.path.dirname(f"{fname}.bin")
        self.stage_sigs["cam.file_name"] = os.path.basename(f"{fname}.bin")

        mode = self.cam.staging_mode.get()
        if mode == "fast":
            self.stage_sigs = {}
            self.stage_sigs["cam.acquire"] = 0
            self.stage_sigs["cam.acquire_time"] = 20e-6
            self.stage_sigs["cam.image_mode"] = "2 Bit, Zero-Deadtime"
            self.stage_sigs["cam.trigger_mode"] = "ZDT Fixed Time"
            self.stage_sigs["cam.num_images"] = 100_000  # "_" is a visual separator
            self.stage_sigs["cam.corrections"] = "Enabled"
            self.stage_sigs["cam.data_type"] = "UInt32"
            # TODO: what else is needed?

        # elif mode == "slow":
        #     path = "/Rigaku/bin/destination/RigakuEpics/"
        #     self.stage_sigs = {}
        #     self.stage_sigs["cam.image_mode"] = "16 Bit, 1S"
        #     self.stage_sigs["cam.trigger_mode"] = "Fixed Time"
        #     self.stage_sigs["cam.acquire_time"] = 0.1
        #     self.stage_sigs["cam.num_images"] = 10
        #     self.stage_sigs["cam.data_type"] = "UInt16"
        #     self.stage_sigs["cam.corrections"] = "Disabled"
        #     self.stage_sigs["imm1.auto_increment"] = "Yes"
        #     self.stage_sigs["imm1.num_capture"] = 10
        #     self.stage_sigs["imm1.file_number"] = 1
        #     self.stage_sigs["imm1.file_path"] = path
        #     self.stage_sigs["imm1.file_name"] = "test"
        #     # TODO: what else is needed?

    @property
    def images_received(self):
        """
        Return the number (int) of images captured.
        suggestion:  ``self.immout.num_captured.get()``
        """
        raise NotImplementedError("Must implement in detector-specific subclass.")

    @property
    def plugin_file_name(self):
        """
        return the (base, no path) file name the plugin wrote
        Implement for the DM workflow.
        Not a bluesky "plan" (no "yield from")
        """
        # fname = (
        #     f"{self._file_name}"
        #     f"_{dm_pars.data_begin.get():05.0f}"
        #     f"-{dm_pars.data_end.get():05.0f}"
        #     ".bin"
        # )

        fname = (
            f"{self._file_name}"
            f"_{1:05.0f}"
            f"-{100000:05.0f}"
            ".bin"
        )

        return fname
        # return os.path.basename(self.immout.full_file_name.get())
        # return f"{self.batch_name.get()}.bin"

    def xpcs_loop(self, *args, **kwargs):
        """
        Combination of `xpcs_pre_start_LAMBDA` and `user_xpcs_loop_LAMBDA`
        see: https://github.com/aps-8id-trr/ipython-8idiuser/issues/107
        """
        # logger.debug(f"xpcs_loop({args})")
        raise NotImplementedError("must override in subclass")


# wait a bit for all previous PV connections to complete
_delay = 2.5  # empirical determination (1.0 is too short, 2 tests OK)
logger.info("Sleeping for %s seconds before creating adrigaku object.", _delay)
ttime.sleep(_delay)

adrigaku = RigakuUfxcDetector(IOC_PREFIX, name="adrigaku")