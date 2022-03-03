"""
Bluesky support for XPCS X-Spectrum Lambda2M EPICS IOC

see: https://x-spectrum.de/products/lambda

GUI: /xorApps/ui/8id/lambda2m/ui/start_caQtDM_lambda2m

* detector name: -tba-
* detector number: -tba-
"""

__all__ = [
    "lambda2m",
]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd.areadetector import ADComponent
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import EpicsSignal
from ophyd.areadetector import EpicsSignalRO
from ophyd.areadetector import EpicsSignalWithRBV
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import CodecPlugin_V34
from ophyd.areadetector.plugins import HDF5Plugin_V34
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
import pathlib


PV_PREFIX = "8idLambda2m:"

TEST_IMAGE_DIR = "test"
AD_IOC_MOUNT_PATH = pathlib.Path("/extdisk")
BLUESKY_MOUNT_PATH = pathlib.Path("/home/8ididata")

# MUST end with a `/`
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / TEST_IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / TEST_IMAGE_DIR}/"


class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin_V34):
    """
    Add data acquisition methods to HDF5Plugin.

    * ``stage()`` - prepare device PVs befor data acquisition
    * ``unstage()`` - restore device PVs after data acquisition
    * ``generate_datum()`` - coordinate image storage metadata
    """


class MyStatsPlugin(StatsPlugin_V34):
    """Update for latest changes in attributes."""

    # TODO: contribute back to ophyd (as of AD v3.9.0)
    ts_acquiring = ADComponent(EpicsSignalRO, "TS:TSAcquiring")
    ts_current_point = ADComponent(EpicsSignal, "TS:TSCurrentPoint")
    ts_num_points = ADComponent(EpicsSignal, "TS:TSNumPoints")
    ts_read = ADComponent(EpicsSignal, "TS:TSRead", string=True)  # 0=Done 1=Read


class Lambda2mCam(CamBase):
    """
    X-Spectrum Lambda 2M detector.

    https://x-spectrum.de/products/lambda
    """

    _html_docs = ["Lambda2mCam.html"]

    # TODO: contribute back to ophyd (as of AD v3.9.0)
    detector_state = ADComponent(EpicsSignalRO, "DetectorState_RBV", kind="config")
    lambda_state = ADComponent(EpicsSignalRO, "LambdaState", kind="config")

    firmware_version = ADComponent(EpicsSignalRO, "FirmwareVersion_RBV", kind="config")
    operating_mode = ADComponent(EpicsSignalWithRBV, "OperatingMode", kind="config")
    serial_number = ADComponent(EpicsSignalRO, "SerialNumber_RBV", kind="config")
    temperature = ADComponent(EpicsSignalWithRBV, "Temperature", kind="config")

    energy_threshold = ADComponent(EpicsSignalWithRBV, "EnergyThreshold", kind="config")
    dual_threshold = ADComponent(EpicsSignalWithRBV, "DualThreshold", kind="config")
    dual_mode = ADComponent(EpicsSignalWithRBV, "DualMode", kind="config")

    pool_max_buffers = None  # REMOVED


class XpcsLambda2mDetector(DetectorBase):
    """XPCS configuration of the Lambda 2M."""

    _html_docs = ["Lambda2MDoc.html"]

    cam = ADComponent(Lambda2mCam, "cam1:")
    codec1 = ADComponent(CodecPlugin_V34, "Codec1:")

    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin_V34, "image1:")
    stats1 = ADComponent(MyStatsPlugin, "Stats1:")
    stats2 = ADComponent(MyStatsPlugin, "Stats2:")

try:
    lambda2m = XpcsLambda2mDetector(
        PV_PREFIX,
        name="lambda2m",
        labels=["lambda", "areadetectors", "detectors"]
    )

except TimeoutError:
    logger.warning(
        "Could not connect Lambda 2M detector"
        f" with prefix  {PV_PREFIX}"
    )
    lambda2m = None

# see Pilatus example for staging ideas
# https://bcda-aps.github.io/apstools/examples/_ad__pilatus.html#pilatus-support-code
# OR, configure settings in plan code
