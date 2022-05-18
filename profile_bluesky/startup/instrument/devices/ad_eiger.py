"""
Eiger area detector. Definition borrowd from Gilberto:
https://github.com/APS-4ID-POLAR/ipython-polar/blob/master/profile_bluesky/startup/instrument/devices/ad_eiger.py
"""

from pathlib import PurePath
from time import time as ttime
from ophyd import (Component, ADComponent, EigerDetectorCam, DetectorBase,
                   Staged, EpicsSignal, Signal, Kind, Device)
from ophyd.areadetector.base import EpicsSignalWithRBV
from ophyd.signal import EpicsSignalRO
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.areadetector.plugins import ROIPlugin_V34, StatsPlugin_V34
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.utils.epics_pvs import set_and_wait
from apstools.utils import run_in_thread
from time import sleep
from os.path import join, isdir
from ..session_logs import logger
logger.info(__file__)

# TODO: Change these paths.
LAMBDA_FILES_ROOT = "/extdisk/4idd/"
BLUESKY_FILES_ROOT = "/home/sector4/4idd/bluesky_images"
TEST_IMAGE_DIR = "%Y/%m/%d/"

# EigerDetectorCam inherits FileBase, which contains a few PVs that were
# removed from AD after V22: file_number_sync, file_number_write,
# pool_max_buffers.
class LocalEigerCam(EigerDetectorCam):
    file_number_sync = None
    file_number_write = None
    pool_max_buffers = None

    wait_for_plugins = ADComponent(EpicsSignal, 'WaitForPlugins', string=True)
    file_path = ADComponent(EpicsSignal, 'FilePath', string=True)
    create_directory = ADComponent(EpicsSignal, "CreateDirectory")


class TriggerDetectorState(TriggerBase):
    """
    This trigger mixin class takes one acquisition per trigger.
    """
    _status_type = ADTriggerStatus

    def __init__(self, *args, image_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        if image_name is None:
            image_name = '_'.join([self.name, 'image'])
        self._image_name = image_name
        # TODO: change the detector status PV
        self._detector_status = self.cam.array_counter
        self._acquisition_signal = self.cam.acquire

    def setup_trigger(self):
        # Stage signals
        #TODO: change these!
        self.cam.stage_sigs["trigger_mode"] = "Internal Enable"
        self.cam.stage_sigs["manual_trigger"] = "Enable"
        self.cam.stage_sigs["num_images"] = 1
        self.cam.stage_sigs["num_exposures"] = 1
        self.cam.stage_sigs["num_triggers"] = int(1e5)

    def stage(self):
        super().stage()
        self._detector_status.subscribe(self._acquire_changed)

    def unstage(self):
        super().unstage()
        self._image_count.clear_sub(self._acquire_changed)
        # set_and_wait(self.cam.acquire, 0) # Not sure this is needed.

    def trigger(self):
        "Trigger one acquisition."
        if self._staged != Staged.yes:
            raise RuntimeError("This detector is not ready to trigger."
                               "Call the stage() method before triggering.")

        self._status = self._status_type(self)
        self._acquisition_signal.put(1, wait=False)
        self.dispatch(self._image_name, ttime())
        return self._status

    def _acquire_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        # TODO: This logic needs to be updated depending on which
        # PV we are using. Something like this:
        # if (old_value != 0) and (value == 0):
        #     # Negative-going edge means an acquisition just finished.
        #     ttime.sleep(self._sleep_time)
        #     self._status.set_finished()
        #     self._status = None
        if value > old_value:  # There is a new image!
            self._status.set_finished()
            self._status = None


class MyHDF5Plugin(FileStoreHDF5SingleIterativeWrite, HDF5Plugin_V34):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5_Eiger500k_APS8ID'


class LocalEigerDetectorBase(DetectorBase):

    # TODO: Do you need rois and stats?
    # TODO: Any other plugins? codec? proc?
    _default_configuration_attrs = ('roi1', 'roi2', 'roi3', 'roi4')
    _default_read_attrs = ('cam', 'file', 'stats1', 'stats2', 'stats3',
                           'stats4')

    _html_docs = ['EigerDoc.html']
    cam = Component(LocalEigerCam, 'cam1:')

    hdf1 = Component(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=join(EIGER_FILES_ROOT, IMAGE_DIR),
        read_path_template=join(BLUESKY_FILES_ROOT, IMAGE_DIR),
        kind='normal'
    )

    # ROIs
    roi1 = Component(ROIPlugin_V34, 'ROI1:')
    roi2 = Component(ROIPlugin_V34, 'ROI2:')
    roi3 = Component(ROIPlugin_V34, 'ROI3:')
    roi4 = Component(ROIPlugin_V34, 'ROI4:')

    # ROIs stats
    stats1 = Component(StatsPlugin_V34, "Stats1:")
    stats2 = Component(StatsPlugin_V34, "Stats2:")
    stats3 = Component(StatsPlugin_V34, "Stats3:")
    stats4 = Component(StatsPlugin_V34, "Stats4:")

    def __init__(
        self, *args, write_path_template="", read_path_template="", **kwargs
    ):
        super().__init__(*args, **kwargs)

        if write_path_template != "":
            self._write_path_template = write_path_template
        if read_path_template != "":
            self._read_path_template = read_path_template

    def default_kinds(self):

        # TODO: This is setting A LOT of stuff as "configuration_attrs", should
        # be revised at some point.

        # Some of the attributes return numpy arrays which Bluesky doesn't
        # accept: configuration_names, stream_hdr_appendix,
        # stream_img_appendix.
        _remove_from_config = (
            "file_number_sync",  # Removed from EPICS
            "file_number_write",  # Removed from EPICS
            "pool_max_buffers",  # Removed from EPICS
            # all below are numpy.ndarray
            "configuration_names",
            "stream_hdr_appendix",
            "stream_img_appendix",
            "dim0_sa",
            "dim1_sa",
            "dim2_sa",
            "nd_attributes_macros",
            "dimensions",
            'asyn_pipeline_config',
            'dim0_sa',
            'dim1_sa',
            'dim2_sa',
            'dimensions',
            'histogram',
            'ts_max_value',
            'ts_mean_value',
            'ts_min_value',
            'ts_net',
            'ts_sigma',
            'ts_sigma_xy',
            'ts_sigma_y',
            'ts_total',
            'ts_timestamp',
            'ts_centroid_total',
            'ts_eccentricity',
            'ts_orientation',
            'histogram_x',
        )

        self.cam.configuration_attrs += [
            item for item in EigerDetectorCam.component_names if item not in
            _remove_from_config
        ]

        self.cam.read_attrs += ["num_images_counter"]

        # TODO: Do we need rois and stats?
        for name in self.component_names:
            comp = getattr(self, name)
            if isinstance(comp, (ROIPlugin_V34, StatsPlugin_V34)):
                comp.configuration_attrs += [
                    item for item in comp.component_names if item not in
                    _remove_from_config
                ]
            if isinstance(comp, StatsPlugin_V34):
                comp.total.kind = Kind.hinted
                comp.read_attrs += ["max_value", "min_value"]

    def default_settings(self):
        # TODO: Change these!
        self.cam.num_triggers.put(1)
        self.cam.manual_trigger.put("Disable")
        self.cam.trigger_mode.put("Internal Enable")
        self.cam.acquire.put(0)
        self.cam.wait_for_plugins.put("Yes")
        self.cam.create_directory.put(-1)
        self.cam.fw_compression.put("Enable")
        self.cam.fw_num_images_per_file.put(1)
        self.setup_trigger()


class EigerDetector(TriggerDetectorState, LocalEigerDetectorBase):
    pass
