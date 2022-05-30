"""
Eiger area detector. Definition borrowed from Gilberto:
https://github.com/APS-4ID-POLAR/ipython-polar/blob/master/profile_bluesky/startup/instrument/devices/ad_eiger.py
"""

from ..session_logs import logger
from apstools.devices import AD_EpicsHdf5FileName
import itertools
from ophyd import (
    Component,
    ADComponent,
    EigerDetectorCam,
    DetectorBase, Staged,
    EpicsSignal
)
from ophyd.areadetector.filestore_mixins import (
    FileStoreBase, FileStoreIterativeWrite
)
from ophyd.areadetector.plugins import (
    StatsPlugin_V34, HDF5Plugin_V34, CodecPlugin_V34
)
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.utils.epics_pvs import set_and_wait
from pathlib import PurePath
from time import time as ttime

logger.info(__file__)

EIGER_FILES_ROOT = PurePath("/home/8ididata/2022-1/bluesky202205/")
BLUESKY_FILES_ROOT = PurePath("/home/8ididata/2022-1/bluesky202205/")
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

    # TODO: The setup_trigger function might be unnecessary because this is
    # handled by staging_setup_DM defined below.
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
            self._status.set_finished()
            self._status = None


class AD_EpicsHdf5FileName_8IDI(AD_EpicsHdf5FileName):
    def stage(self):
        # Ensure we do not have an old file open.
        set_and_wait(self.capture, 0)

        # Stage signals, which include file name and path,
        # see staging_setup_DM below.
        FileStoreBase.stage(self)

        # Setup the staged file name and path in the database
        filename, read_path, _ = self.make_filename()
        template = self.file_template.get()
        self._fn = template % (read_path, filename)
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError(
                f"Path {self.file_path.get()} does not exist on IOC."
            )

        self._point_counter = itertools.count()

        # from FileStoreHDF5.stage()
        res_kwargs = {"frame_per_point": self.get_frames_per_point()}
        self._generate_resource(res_kwargs)

    def generate_datum(self, key, timestamp, datum_kwargs):
        """Generate a uid and cache it with its key for later insertion."""
        template = self.file_template.get()
        filename, read_path, write_path = self.make_filename()
        hdf5_file_name = template % (read_path, filename)

        logger.debug("make_filename: %s", hdf5_file_name)
        logger.debug("write_path: %s", write_path)
        return super(AD_EpicsHdf5FileName, self).generate_datum(
            key, timestamp, datum_kwargs
        )


class myHdf5EpicsIterativeWriter(
    AD_EpicsHdf5FileName_8IDI, FileStoreIterativeWrite
):
    pass


class MyHDF5Plugin(HDF5Plugin_V34, myHdf5EpicsIterativeWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Using the default bluesky HDF5 handler.
        self.filestore_spec = 'AD_HDF5'

    image_dir = IMAGE_DIR


class LocalEigerDetectorBase(DetectorBase):

    # TODO: Might want to add rois and stats to the scan.
    # _default_configuration_attrs = ('roi1', 'roi2', 'roi3', 'roi4')
    _default_read_attrs = ('cam', 'hdf1', 'codec1')
    # 'stats1', 'stats2', 'stats3', 'stats4'

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
        # TODO: Do you need to change the related PVs in the detector? Note
        # that acquire_time and acquire_period is not currently used.
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

        # QZ added this to remove automatic FileNumber append and to comply
        # with DM transfer for Rigaku format
        self.hdf1.stage_sigs["file_template"] = "%s%s.h5"

        # This must always come last
        self.hdf1.stage_sigs["capture"] = self.hdf1.stage_sigs.pop('capture')
        print(
            f"({self.__class__.__name__}): hdf1 stage_sigs="
            f"{self.hdf1.stage_sigs}"
        )

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

    # TODO: Add rois and stats?
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
        capture = self.hdf1.stage_sigs.pop('capture')
        self.hdf1.stage_sigs["capture"] = capture

    # TODO: Decide which PVs you want to save in the run as "config", and which
    # you want to save every point (kind="normal") or plot (kind="hinted")
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
                comp.total.kind = "hinted"
                comp.read_attrs += ["max_value", "min_value"]

    # TODO: This function might be useless if you add all default values to
    # staging_setup_DM().
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
