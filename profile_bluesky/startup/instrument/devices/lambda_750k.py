"""
X-Spectrum Lambda 750K area detector (EPICS)

* detector name: LAMBDA
* detector number: 25

Mimics an ophyd.areaDetector object without subclassing it.
"""

__all__ = [
    "lambdadet",
]

from instrument.session_logs import logger

logger.info(__file__)

from .ad_acquire_detector_base import AD_AcquireDetectorBase
from .ad_acquire_detector_base import AD_AcquireDetectorCamBase
from .ad_imm_plugins import IMM_DeviceMixinBase
from .data_management import DM_DeviceMixinAreaDetector
from .data_management import dm_pars
from .shutters import shutter
from .shutters import shutter_override
from .soft_glue_fpga import pvDELAY_A
from .soft_glue_fpga import pvDELAY_B
from .soft_glue_fpga import sg_num_frames
from .soft_glue_fpga import soft_glue
from bluesky import plan_stubs as bps
from ophyd import Component
from ophyd import Device
from ophyd import DeviceStatus
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import Signal
import itertools
import os
import time
import uuid


LAMBDA_750K_IOC_PREFIX = "8LAMBDA1:"


class Lambda750kCamLocal(AD_AcquireDetectorCamBase, Device):
    """
    local interface to the ADLambda 750k cam1 plugin
    """

    # implement just the parts needed by our data acquisition
    acquire = Component(EpicsSignalWithRBV, "Acquire", trigger_value=1, kind="config")
    acquire_period = Component(EpicsSignalWithRBV, "AcquirePeriod", kind="config")
    acquire_time = Component(EpicsSignalWithRBV, "AcquireTime", kind="config")
    array_callbacks = Component(EpicsSignalWithRBV, "ArrayCallbacks", kind="config")
    num_images = Component(EpicsSignalWithRBV, "NumImages")
    # blocking_callbacks = Component(EpicsSignalWithRBV, "BlockingCallbacks")

    bad_frame_counter = Component(EpicsSignal, "BadFrameCounter", kind="config")
    config_file_path = Component(
        EpicsSignal, "ConfigFilePath", string=True, kind="config"
    )
    data_type = Component(EpicsSignalWithRBV, "DataType", kind="config")
    firmware_version = Component(
        EpicsSignalRO, "FirmwareVersion_RBV", string=True, kind="config"
    )
    image_mode = Component(EpicsSignalWithRBV, "ImageMode", kind="config")
    operating_mode = Component(EpicsSignalWithRBV, "OperatingMode", kind="config")
    serial_number = Component(
        EpicsSignalRO, "SerialNumber_RBV", string=True, kind="config"
    )
    detector_state = Component(
        EpicsSignalRO, "DetectorState_RBV", kind="config", string=True
    )
    state = Component(EpicsSignalRO, "LambdaState", kind="config", string=True)
    status_msg = Component(
        EpicsSignalRO, "StatusMessage_RBV", kind="config", string=True
    )
    temperature = Component(EpicsSignalWithRBV, "Temperature", kind="config")
    trigger_mode = Component(EpicsSignal, "TriggerMode", kind="config")

    array_size_x = Component(EpicsSignalRO, "ArraySizeX_RBV", kind="config")
    array_size_y = Component(EpicsSignalRO, "ArraySizeY_RBV", kind="config")

    EXT_TRIGGER = 0
    LAMBDA_OPERATING_MODE = 0  # (0, 'ContinuousReadWrite', 1, 'TwentyFourBit')

    # constants
    MODE_TRIGGER_INTERNAL = 0
    MODE_TRIGGER_EXTERNAL_PER_SEQUENCE = 1
    MODE_TRIGGER_EXTERNAL_PER_FRAME = 2
    MODE_MULTIPLE_IMAGE = 1

    @property
    def getBadFrameCount(self):
        """
        """
        # from SPEC macro: ccdget_Lambda_BadFrameCount
        return self.bad_frame_counter.get()

    @property
    def getDataType(self):
        # from SPEC macro: ccdget_DataType_ad
        return self.data_type.get()

    @property
    def getOperatingMode(self):
        return self.operating_mode.get()

    def setDataType(self, value):
        """
        value: 0-7 for ('Int8', 'UInt8', 'Int16', 'UInt16', 'Int32', 'UInt32', 'Float32', 'Float64')
        """
        # from SPEC macro: ccdset_DataType_ad
        yield from bps.mv(self.data_type, value)

    def setImageMode(self, mode):
        """
        mode = 0, 1 for ('Single', 'Multiple')
        """
        # from SPEC macro: ccdset_ImageMode
        if mode not in (0, 1):
            raise ValueError(f"image mode {mode} not allowed, must be one of 0, 1")
        yield from bps.mv(self.image_mode, mode)

    def setOperatingMode(self, mode):
        """
        mode = 0, 1 for ContinuousReadWrite(12-bit), TwentyFourBit
        """
        # from SPEC macro: ccdset_OperatingMode_Lambda
        if mode not in (0, 1):
            raise ValueError(
                f"operating mode {mode} not allowed, must be one of 0, 1"
                " (0='ContinuousReadWrite', 1='TwentyFourBit')"
            )
        if self.operating_mode.get() != mode:
            yield from bps.mv(self.operating_mode, mode)
            # yield from bps.sleep(5.0)     # TODO: still needed?
            logger.info(f"Lambda Operating Mode switched to: {mode}")

        if self.operating_mode.get() == 1:
            yield from self.setDataType(3)  # 3: UInt16
            data_type = self.getDataType
            logger.info("Lambda DataType switched to: {data_type}")

    def setTime(self, exposure_time, exposure_period):
        """
        set exposure time and period
        """
        # from SPEC macro: ccdset_time_Lambda
        # set exp time always regardless of any mode
        yield from bps.mv(self.acquire_time, exposure_time)
        # yield from bps.sleep(0.05)

        extra = 1e-3  # 1 ms is typical for period
        extra += 100e-6  # extra 100 us for 24-bit mode (empirical)

        # set period based on the mode
        if self.getOperatingMode == 0:  # continuous read/write mode
            yield from bps.mv(self.acquire_period, exposure_time)
        else:
            yield from bps.mv(
                self.acquire_period, max(exposure_period, exposure_time + extra)
            )
        # yield from bps.sleep(0.05)

        if self.EXT_TRIGGER > 0 and self.getOperatingMode == 0:
            # this should work for single-trigger per sequence as well
            yield from bps.mv(
                pvDELAY_B, 1e-4
            )  # for softglue trigger generation (shorter than the fastest frame time)
            # yield from bps.sleep(0.05)
            yield from bps.mv(
                pvDELAY_A, exposure_time
            )  # AcquirePeriod in area detector
            # yield from bps.sleep(0.05)

        elif self.EXT_TRIGGER == 2 and self.getOperatingMode == 1:
            yield from bps.mv(pvDELAY_B, exposure_time)  # AcquireTime in area detector
            # yield from bps.sleep(0.05)
            yield from bps.mv(
                pvDELAY_A, max(exposure_period, exposure_time + extra)
            )  # AcquirePeriod in area detector
            # yield from bps.sleep(0.05)

        elif self.EXT_TRIGGER == 1 and self.getOperatingMode == 1:
            # important thing to be aware:
            # lambda does not support acquire_period in any way,
            # except with trigger per frame mode
            yield from bps.mv(pvDELAY_B, exposure_time)  # AcquireTime in area detector
            # yield from bps.sleep(0.05)
            yield from bps.mv(
                pvDELAY_A, exposure_time + 0.0011
            )  # AcquirePeriod in area detector
            # yield from bps.sleep(0.05)

        if self.EXT_TRIGGER > 0:
            if (exposure_period - exposure_time) >= 0.45 and exposure_time >= 0.05:
                yield from bps.mv(
                    soft_glue.set_shtr_sig_pulse_tr_mode,
                    "0",
                    soft_glue.send_det_sig_pulse_tr_mode,
                    "0",
                    shutter_override,
                    0,
                )
                msg = "REGULAR...opens and closes during exposure"
            else:
                # prevents user from operating shutter for fast duty cycle
                yield from bps.mv(
                    soft_glue.set_shtr_sig_pulse_tr_mode,
                    "1",
                    soft_glue.send_det_sig_pulse_tr_mode,
                    "1",
                    shutter_override,
                    1,
                )
                msg = "BURST...Stays open for the full sequence"
            logger.info("Setting Shutter Mode for Detector ===> " + msg)

    def setTriggerMode(self, mode):
        """
        mode = 0,1,2 for Internal, External_per_sequence, External_per_frame
        note: mode = 3 ("Gating_Mode", permitted by EPICS record) is not supported here
        """
        # from SPEC macro: ccdset_TriggerMode_Lambda
        if mode not in (0, 1, 2):
            raise ValueError(f"trigger mode {mode} not allowed, must be one of 0, 1, 2")
        yield from bps.mv(self.trigger_mode, mode)

    def setup_modes(self, num_triggers):
        """
        set up modes accordingly, based on self.EXT_TRIGGER
        """
        # from SPEC macro: Lambda_modes_setup

        yield from self.setOperatingMode(self.LAMBDA_OPERATING_MODE)

        if self.EXT_TRIGGER == 0:
            yield from self.setup_trigger_mode_internal()
        elif self.EXT_TRIGGER == 2:
            yield from self.setup_trigger_mode_external()
        else:
            yield from bps.null()

        yield from self.setTriggerMode(self.EXT_TRIGGER)
        # TODO: shutteroff_default
        if self.EXT_TRIGGER == self.MODE_TRIGGER_EXTERNAL_PER_FRAME:
            action = "OPEN AND CLOSE DURING"
            yield from self.setup_trigger_logic_external(num_triggers)
        else:  # self.MODE_TRIGGER_INTERNAL and self.MODE_TRIGGER_EXTERNAL_PER_SEQUENCE
            action = "REMAIN OPEN THROUGH"
        logger.info(f"Shutter will *{action}* the Acquisition...")

    def setup_trigger_logic_external(self, num_triggers):
        """
        configure the number of triggers to be expected
        """
        # from SPEC macro: external_trigger_logic_setup_Data_Lambda

        # Set number of frames in SGControl1 depending on the mode
        if self.getOperatingMode == 0:
            num_triggers += 1
        logger.debug(f"num_triggers = {num_triggers}")
        yield from bps.mv(sg_num_frames, num_triggers)

        yield from bps.mv(
            soft_glue.send_ext_pulse_tr_sig_to_trig, "1"
        )  # external trigger
        #####shutter burst/regular mode and the corresponding trigger pulses are selected separately###

    def setup_trigger_mode_external(self):
        """
        configure EPICS area detector for external triggering

        user can change chosen image mode via `self.EXT_TRIGGER`
        """
        # from SPEC macro: external_trigger_mode_setup_Lambda
        yield from self.setTriggerMode(self.EXT_TRIGGER)
        yield from self.setImageMode(self.MODE_MULTIPLE_IMAGE)

    def setup_trigger_mode_internal(self):
        """
        configure EPICS area detector for internal triggering, multiple images
        """
        # from SPEC macro: internal_trigger_mode_setup_Lambda
        yield from self.setTriggerMode(self.MODE_TRIGGER_INTERNAL)
        yield from self.setImageMode(self.MODE_MULTIPLE_IMAGE)


class StatsLocal(Device):
    """
    local interface to the Stats plugin
    """

    # implement just the parts needed by our data acquisition
    mean_value = Component(EpicsSignalWithRBV, "MeanValue", kind="config")


class ExternalFileReference(Signal):
    """
    A pure software signal where a Device can stash a datum_id
    """

    def __init__(self, *args, shape, **kwargs):
        super().__init__(*args, **kwargs)
        self.shape = shape

    def describe(self):
        res = super().describe()
        res[self.name].update(
            dict(external="FILESTORE:", dtype="array", shape=self.shape)
        )
        return res


class Lambda750kLocal(IMM_DeviceMixinBase, DM_DeviceMixinAreaDetector, AD_AcquireDetectorBase):
    """
    local interface to the Lambda 750k detector
    """

    qmap_file = "Lambda_qmap.h5"

    # implement just the parts needed by our data acquisition
    detector_number = 25  # 8-ID-I numbering of this detector

    cam = Component(Lambda750kCamLocal, "cam1:")
    stats1 = Component(StatsLocal, "Stats1:")
    image = Component(ExternalFileReference, value="", shape=[])

    # 8LAMBDA1:set1:userScript1 is a luascript record
    # lua_A = Component(EpicsSignal, "set1:userScript.A", kind="config") # TODO: where is this PV?

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._assets_docs_cache = []

    @property
    def chk_ccdc(self):
        """
        check if there is a pseudo counter "ccdc" configured in spec

        Look through all the counters and report if
        any one of them is named `ccdc`.
        """
        # FIXME: We don't have a counter named "ccdc"
        return False

    @property
    def getCounts(self):
        """
        get counts from IMM plugins
        """
        # from SPEC macro: ccd_getcounts_ad_Lambda
        # FIXME: this routine needs attention

        # BUT, this is only used when there is a
        # pseudo-counter named "ccdc" (that's what chk_ccdc() does)
        if self.chk_ccdc:
            if dm_pars.compression.get() == 1:
                return self.imm1.num_pixels.get()
            else:
                return self.stats1.mean_value.get()

    @property
    def images_received(self):
        return self.imm1.num_captured.get()

    @property
    def plugin_file_name(self):
        """
        return the file name the plugin wrote
        """
        # cut the path from file name
        return os.path.basename(self.imm1.full_file_name.get())
        # return os.path.join(self.imm1.file_path.get(), self.imm1.file_name.get())

    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the detector's stage_sigs for acquisition with the DM workflow
        """
        if len(args) != 5:
            raise IndexError(
                f"expected 5 parameters, received {len(args)}: args={args}"
            )
        self._file_path = args[0]
        self._file_name = args[1]
        num_images = args[2]
        acquire_time = args[3]
        acquire_period = args[4]
        # logger.debug(f"staging_setup_DM({args})")

        self.cam.stage_sigs["num_images"] = num_images
        # replaced by: self.cam.setTime(acquire_time, acquire_period)
        self.imm1.stage_sigs["enable"] = 1
        self.imm1.stage_sigs["blocking_callbacks"] = "Yes"
        self.imm1.stage_sigs["parent.cam.array_callbacks"] = 1
        self.imm1.stage_sigs["file_path"] = self._file_path
        self.imm1.stage_sigs["file_name"] = self._file_name
        self.imm1.stage_sigs["num_capture"] = num_images
        self.imm1.stage_sigs["file_number"] = 1
        self.imm1.stage_sigs["capture"] = 1

    def stage(self):
        super().stage()
        root = os.path.join("/", "home", "8ididata/")
        # print(root)
        # if self._file_path.startswith("/data/"):
        #     self._file_path = self._file_path[len("/data/") :]
        #     print(self._file_path)
        # elif self._file_path.startswith("/home/8ididata/"):
        #     self._file_path = self._file_path[len("/home/8ididata/") :]

        fname = (
            f"{self._file_name}"
            f"_{dm_pars.data_begin.get():05.0f}"
            f"-{dm_pars.data_end.get():05.0f}"
            ".imm"
        )
        full_name = os.path.join(root, self._file_path, fname)
        print(full_name)
        logger.info(f"full_name: {full_name}")
        self._resource_uid = str(uuid.uuid4())
        resource_doc = {
            "uid": self._resource_uid,
            "spec": "IMM",
            "resource_path": os.path.join(self._file_path, fname),
            "root": root,
            "resource_kwargs": {"frames_per_point": self.get_frames_per_point()},
            "path_semantics": "posix",
            # can't add new stuff, such as: 'full_name': full_name,
        }
        self._datum_counter = itertools.count()
        self.image.shape = [
            self.get_frames_per_point(),
            self.cam.array_size_y.get(),
            self.cam.array_size_x.get(),
        ]
        self._assets_docs_cache.append(("resource", resource_doc))

    def trigger(self):
        "trigger device acquisition and return a status object"
        start_value = 1
        done_value = 0

        status = DeviceStatus(self)

        def watch_state(value, old_value, **kwargs):
            """
            close the shutter once self.cam.state != "RECEIVING_IMAGES"
            """
            logger.debug(f"lambdadet.cam.state={value}")
            logger.debug(f"old value={old_value}")
            logger.debug(f"capture={self.imm1.capture.get()}")
            if value in (5, "FINISHED", 6, "PROCESSING_IMAGES") and old_value in (
                4,
                "RECEIVING_IMAGES",
            ):
                shutter.close()
                self.cam.state.clear_sub(watch_state)
                logger.debug("closed shutter")

        def watch_acquire(value, old_value, **kwargs):
            """
            watch the acquire button, waiting for it to Stop (0)
            """
            if value == done_value and old_value != value:
                self.imm1.capture.clear_sub(watch_acquire)
                logger.info("watch_acquire() method ends")
                logger.info(f"cam.acquire.get()={self.cam.acquire.get()}")
                logger.info(f"imm1.capture.get()={self.imm1.capture.get()}")
                logger.info(
                    f"imm1.num_captured.get()={self.imm1.num_captured.get()}"
                )
                status._finished()
                shutter.close()
                logger.info(f"status={status}")

        shutter.open()
        time.sleep(0.005)  # wait for the shutter to move out of the way
        self.cam.state.subscribe(watch_state)
        self.imm1.capture.subscribe(watch_acquire)
        # for plugin in (self.imm0, self.imm1, self.imm2):
        #     plugin.capture.put(1, wait=False)
        self.imm1.capture.put(1, wait=False)
        self.imm1.capture.put(1, wait=False)
        self.cam.acquire.put(start_value, wait=False)
        if self.cam.EXT_TRIGGER > 0:
            # t0 = time.time()
            # while soft_glue.acquire_ext_trig_status.get() != 1:
            #     # detector reports (to soft glue) when it is ready for frame triggers
            #     # Lambda manufacturer recommends this is 0.5 sec or so
            #     time.sleep(0.025)
            #     t = time.time() - t0
            #     if t > 5:
            #         emsg = f"Lambda detector not ready for frame triggers after {t:.3f}s"
            #         raise TimeoutError(emsg)
            # t = time.time() - t0
            # if t > .2e-10:
            #     logger.debug(f"waited {t:.3f}s for detector to become ready for frame triggers")
            time.sleep(0.5)  # manufacturer's minimum recommendation
        index = next(self._datum_counter)
        datum_id = f"{self._resource_uid}/{index}"
        datum_doc = {
            "resource": self._resource_uid,
            "datum_id": datum_id,
            "datum_kwargs": {"index": index},
        }
        self.image.set(datum_id)
        self._assets_docs_cache.append(("datum", datum_doc))

        return status

    def collect_asset_docs(self):
        cache = self._assets_docs_cache.copy()
        yield from cache
        self._assets_docs_cache.clear()

    def get_frames_per_point(self):
        return self.cam.num_images.get()


try:
    lambdadet = Lambda750kLocal(
        LAMBDA_750K_IOC_PREFIX, name="lambdadet", labels=["lambda",]
    )

    lambdadet.read_attrs += ["imm1", "image"]

except TimeoutError:
    logger.warning(
        "Could not connect Lambda 750K detector"
        f" with prefix  {LAMBDA_750K_IOC_PREFIX}"
    )
    lambdadet = None
