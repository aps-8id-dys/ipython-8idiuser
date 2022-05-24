"""
Eiger area detector. Definition borrowed from Gilberto:
https://github.com/APS-4ID-POLAR/ipython-polar/blob/master/profile_bluesky/startup/instrument/devices/ad_eiger.py
"""

from xml.dom.expatbuilder import parseString
from ..session_logs import logger
from apstools.devices import AD_EpicsHdf5FileName
from apstools.utils import run_in_thread
import itertools
from ophyd import (Component, ADComponent, EigerDetectorCam, DetectorBase, Staged, EpicsSignal, Signal, Kind, Device)
from ophyd.areadetector.base import EpicsSignalWithRBV
from ophyd.areadetector.filestore_mixins import FileStoreBase, FileStoreIterativeWrite, FileStoreHDF5SingleIterativeWrite
from ophyd.areadetector.plugins import ROIPlugin_V34, StatsPlugin_V34, HDF5Plugin_V34, CodecPlugin_V34
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.signal import EpicsSignalRO
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.utils.epics_pvs import set_and_wait
from os.path import join, isdir
from pathlib import PurePath
from time import sleep
from time import time as ttime

logger.info(__file__)



EIGER_FILES_ROOT = PurePath("/home/8ididata/2022-1/bluesky202205/")
BLUESKY_FILES_ROOT = PurePath("/home/8ididata/2022-1/bluesky202205/")
# IMAGE_DIR = "%Y/%m/%d/"
IMAGE_DIR = ""

# EigerDetectorCam inherits FileBase, which contains a few PVs that were
# removed from AD after V22: file_number_sync, file_number_write,
# pool_max_buffers.
class LocalEigerCam(EigerDetectorCam):
    file_number_sync = None
    file_number_write = None
    pool_max_buffers = None
    # Hard-coded to 0 for AD_Acquire
    EXT_TRIGGER = 0

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
        self._detector_status = self.cam.acquire
        self._acquisition_signal = self.cam.acquire

    def setup_trigger(self):
        # Stage signals
        self.cam.stage_sigs["trigger_mode"] = "Internal Series"
        # self.cam.stage_sigs["manual_trigger"] = "Enable"
        # self.cam.stage_sigs["num_images"] = 1
        # self.cam.stage_sigs["num_exposures"] = 1
        # self.cam.stage_sigs["num_triggers"] = int(1e5)

    def stage(self):
        super().stage()
        self._detector_status.subscribe(self._acquire_changed)

    def unstage(self):
        super().unstage()
        self._detector_status.clear_sub(self._acquire_changed)
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
        if (old_value != 0) and (value == 0):
            # Negative-going edge means an acquisition just finished.
            # ttime.sleep(self._sleep_time)
            self._status.set_finished()
            self._status = None
        # if value > old_value:  # There is a new image!
        #     self._status.set_finished()
        #     self._status = None


class myHdf5EpicsIterativeWriter(AD_EpicsHdf5FileName, FileStoreIterativeWrite):
    pass
    # def stage(self):
    #     """
    #     QZ: overrides the override in AD_EpicsHdf5FileName
    #     that allows for writing file name with desired format
    #     """
    #     # Make a filename.
    #     filename, read_path, write_path = self.make_filename()

    #     # Ensure we do not have an old file open.
    #     set_and_wait(self.capture, 0)
    #     # These must be set before parent is staged (specifically
    #     # before capture mode is turned on. They will not be reset
    #     # on 'unstage' anyway.
    #     set_and_wait(self.file_path, write_path)
    #     set_and_wait(self.file_name, filename)
    #     # set_and_wait(self.file_number, 0)

    #     # get file number now since it is incremented during stage()
    #     file_number = self.file_number.get()
    #     # Must avoid parent's stage() since it sets file_number to 0
    #     # Want to call grandparent's stage()
    #     # super().stage()     # avoid this - sets `file_number` to zero
    #     # call grandparent.stage()
    #     FileStoreBase.stage(self)

    #     # AD does the file name templating in C
    #     # We can't access that result until after acquisition
    #     # so we apply the same template here in Python.
    #     template = self.file_template.get()
    #     self._fn = template % (read_path, filename)
    #     self._fp = read_path
    #     if not self.file_path_exists.get():
    #         raise IOError(f"Path {self.file_path.get()} does not exist on IOC.")

    #     self._point_counter = itertools.count()

    #     # from FileStoreHDF5.stage()
    #     res_kwargs = {"frame_per_point": self.get_frames_per_point()}
    #     self._generate_resource(res_kwargs)    


class MyHDF5Plugin(HDF5Plugin_V34, myHdf5EpicsIterativeWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5_Eiger500k_APS8ID'

    image_dir = IMAGE_DIR


class LocalEigerDetectorBase(DetectorBase):

    # _default_configuration_attrs = ('roi1', 'roi2', 'roi3', 'roi4')
    _default_read_attrs = ('cam', 'hdf1', 'codec1',
    # 'stats1', 'stats2', 'stats3', 'stats4'
    )

    #############################################
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

        print(f"({self.__class__.__name__}): num_images={num_images}")
        self.cam.stage_sigs["num_images"] = num_images
        self.hdf1.stage_sigs["num_capture"] = num_images

        print(f"({self.__class__.__name__}): file_name={self._file_name}")
        self.hdf1.stage_sigs["file_name"] = self._file_name

        print(f"({self.__class__.__name__}): hdf.image_dir={self._file_path}")
        self.hdf1.stage_sigs["file_path"] = self._file_path

        # # QZ added this to remove automatic FileNumber append 
        # # and to comply with DM transfer for Rigaku format
        # self.hdf1.stage_sigs["file_template"] = "%s%s.h5"

        # This must always come last
        self.hdf1.stage_sigs["capture"]=self.hdf1.stage_sigs.pop('capture')
        print(f"({self.__class__.__name__}): hdf1 stage_sigs={self.hdf1.stage_sigs}")

    detector_number = 30
    # TODO: add a dummy q map file to test the DM analysis too
    qmap_file = "Lambda_qmap.h5"

    @property
    def plugin_file_name(self):
        """
        return the (base, no path) file name the plugin wrote
        Implement for the DM workflow.
        Not a bluesky "plan" (no "yield from")
        """
        fname = PurePath(self.hdf1.full_file_name.get()).name
    
        return fname

    #############################################

    _html_docs = ['EigerDoc.html']
    cam = Component(LocalEigerCam, 'cam1:')

    codec1 = Component(CodecPlugin_V34, "Codec1:")

    hdf1 = Component(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=str(EIGER_FILES_ROOT / IMAGE_DIR),
        read_path_template=str(BLUESKY_FILES_ROOT / IMAGE_DIR),
        kind='normal'
    )

    # ROIs
    # roi1 = Component(ROIPlugin_V34, 'ROI1:')
    # roi2 = Component(ROIPlugin_V34, 'ROI2:')
    # roi3 = Component(ROIPlugin_V34, 'ROI3:')
    # roi4 = Component(ROIPlugin_V34, 'ROI4:')

    # ROIs stats
    # stats1 = Component(StatsPlugin_V34, "Stats1:")
    # stats2 = Component(StatsPlugin_V34, "Stats2:")
    # stats3 = Component(StatsPlugin_V34, "Stats3:")
    # stats4 = Component(StatsPlugin_V34, "Stats4:")

    def __init__(
        self, *args, write_path_template="", read_path_template="", **kwargs
    ):
        super().__init__(*args, **kwargs)

        if write_path_template != "":
            self.hdf1._write_path_template = write_path_template
        if read_path_template != "":
            self.hdf1._read_path_template = read_path_template
        # 'capture' must always be the last thing in stage list
        capture=self.hdf1.stage_sigs.pop('capture')
        self.hdf1.stage_sigs["capture"]=capture


    def default_kinds(self):

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

        for name in self.component_names:
            comp = getattr(self, name)
            if isinstance(comp, (StatsPlugin_V34)):
                comp.configuration_attrs += [
                    item for item in comp.component_names if item not in
                    _remove_from_config
                ]
            if isinstance(comp, StatsPlugin_V34):
                comp.total.kind = Kind.hinted
                comp.read_attrs += ["max_value", "min_value"]

    def default_settings(self):
        # self.cam.num_triggers.put(1)
        # self.cam.manual_trigger.put("Disable")
        # self.cam.trigger_mode.put("Internal Enable")
        # self.cam.acquire.put(0)
        # self.cam.wait_for_plugins.put("Yes")
        # self.cam.create_directory.put(-1)
        # self.cam.fw_compression.put("Enable")
        # self.cam.fw_num_images_per_file.put(1)
        self.setup_trigger()


class EigerDetector(TriggerDetectorState, LocalEigerDetectorBase):
    pass
