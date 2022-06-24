
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
import pathlib
import ophyd.signal


def AD_Acquire(areadet,
               file_name,
               acquire_time,
               acquire_period,
               num_images,
               path=None,
               submit_xpcs_job=True,
               atten=0,
               md={}):
    """
    acquisition sequence initiating data management workflow

    Outline of acquisition sequence:

    * define cam params such as acquire time, period,
      num images, camera mode
    * define file plugin immout params such as file path,
      file name, num_images, file_number, capture
    * configure scaler channels for monitoring some
      scalers and devices such as temperature
    * trigger area detector while monitoring the
      above params

    PARAMETERS

    areadet obj :
        Area detector object to be used (such as ``lambda2m``).

    file_name str :
        Corresponds to the ARun number.  Could have additional
        metadata appended but no whitespace is expected.
        Unexpected content will be changed before use by
        ``spec_support.APS_DM_8IDI.DM_Workflow.cleanupFilename()``.

    acquire_time float :
        Time (s) to expose each image.

    acquire_period float :
        Time (s) between starting each new image (with ``num_images > 1``).

    num_images int :
        Number of images to acquire.

    path str :
        File directory path used for the data management workflow
        (such as ``/home/8ididata/2022-2/202206``).
        Raises ``ValueError`` if set to ``None``.

    submit_xpcs_job bool :
        Should a job be submitted to the DM worflow for processing?
        Default: ``True``

    atten int :
        ?
        Default: ``0``

    md dict :
        User metadata dictionary to be added to the run.
    """
    logger.info("AD_Acquire starting")

    if path is None:
        raise ValueError("path is not specified."
            "  Typical value: /home/8ididata/2020-3/test202008")

    file_name = dm_workflow.cleanupFilename(file_name)

    # Determine the directory paths to be used:
    file_path = pathlib.Path(path) / file_name
    logger.info(f"file_path = {file_path}")

    plan_args = dict(
        detector_name = areadet.name,
        acquire_time = acquire_time,
        acquire_period = acquire_period,
        num_images = num_images,
        file_name = file_name,
        submit_xpcs_job = str(submit_xpcs_job),
    )
    if atten is not None:
        plan_args["atten"] = atten
    if path is not None:
        plan_args["path"] = path
    md["ARun_number"] = file_name
    md["plan_args"] = plan_args

    atten = atten or Atten1
    assert atten in (Atten1, Atten2)

    # select the detector's number
    yield from bps.mv(dm_pars.detNum, areadet.detector_number)

    # yield from areadet.cam.setup_modes(num_images)
    # yield from areadet.cam.setTime(acquire_time, acquire_period)

    # Ask the devices to configure themselves for this plan.
    # no need to yield here, method does not have "yield from " calls
    # scaler1.staging_setup_DM(acquire_period)
    print(f"(AD_Acquire): num_images={num_images}")
    # TODO: redefine areadet.hdf1.write_path_template?
    areadet.staging_setup_DM(f"{file_path}/", file_name,
            num_images, acquire_time, acquire_period)
    dm_workflow.set_xpcs_qmap_file(areadet.qmap_file)

    # scaler1.select_channels(None)
    monitored_things = [
        timebase,
        pind1,
        pind2,
        Atten1,
        Atten2,
        T_A,
        T_SET,
    ]
    """
        #Timebase,
        pind1,
        pind2,
        pind3,
        pind4,
        pdbs,
        I_APS,
        I0Mon,
        APD,
        cstar_l,
        cstar_h,
        oxygen,
        scaler1_time,
    """

    def timestamp_now():
        return datetime.datetime.now().strftime("%c").strip()

    def make_hdf5_workflow_filename():
        path = file_path
        old_root = pathlib.Path("/data")
        if old_root in path.parents:
            new_root = pathlib.Path("/home/8ididata")
            path = new_root.joinpath(*path.parts[len(old_root.parts):])
            logger.debug(f"modified path: {path}")
            if not path.exists():
                path.mkdir(parents=True)  # TODO: exists_ok=True kwarg?
                logger.debug(f"created path: {path}")
        fname = (
            f"{file_name}"
            f"_{dm_pars.data_begin.get():04.0f}"
            f"-{dm_pars.data_end.get():04.0f}"
        )
        fullname = path / f"{fname}.hdf"
        suffix = 0
        while fullname.exists():
            suffix += 1
            fullname = path / f"{fname}__{suffix:03d}.hdf"
        if suffix > 0:
            logger.info(f"using modified file name: {fullname}")
        return fullname

    def update_metadata_prescan():
        detNum = int(dm_pars.detNum.get())
        det_pars = dm_workflow.detectors.getDetectorByNumber(detNum)
        logger.info(f"detNum={detNum}, det_pars={det_pars}")
        yield from bps.mv(
            # StrReg 2-7 in order
            dm_pars.root_folder, str(file_path),
        )
        # logger.debug("dm_pars.root_folder")

        yield from bps.mv(
            # dm_pars.user_data_folder, os.path.dirname(file_path),   # just last item in path
            dm_pars.user_data_folder, str(file_path.parent),   # FIXME: correct?
        )
        # logger.debug("dm_pars.user_data_folder")

        yield from bps.mv(
            dm_pars.data_folder, file_name,
        )
        # logger.debug("dm_pars.data_folder")

        yield from bps.mv(
            dm_pars.source_begin_datetime, timestamp_now(),
        )
        # logger.debug("dm_pars.source_begin_datetime")

        yield from bps.mv(
            # Reg 121
            dm_pars.source_begin_current, aps.current.get(),
            # Reg 101-110 in order
            dm_pars.roi_x1, 0,
            dm_pars.roi_x2, det_pars["ccdHardwareColSize"]-1,
            dm_pars.roi_y1, 0,
            dm_pars.roi_y2, det_pars["ccdHardwareRowSize"]-1,
            dm_pars.cols, det_pars["ccdHardwareColSize"],
            dm_pars.rows, det_pars["ccdHardwareRowSize"],
            dm_pars.kinetics_state, 0,                  # FIXME: SPEC generated this
            dm_pars.kinetics_window_size, 0,            # FIXME:
            dm_pars.kinetics_top, 0,                    # FIXME:
            dm_pars.attenuation, atten.get(),
        )
        # logger.debug("Reg 121, 101-110 done")

        yield from bps.mv(
            # Reg 111-120 in order
            #dm_pars.dark_begin, -1,            #  edit if detector needs this
            #dm_pars.dark_end, -1,              #  op cit
            dm_pars.data_begin, 1,
            dm_pars.data_end, num_images,
            dm_pars.exposure_time, acquire_time,
            dm_pars.exposure_period, acquire_period,
            # dm_pars.specscan_dark_number, -1,   #  not used, detector takes no darks
            dm_pars.stage_x, detu.x.position,
            dm_pars.stage_z, detu.z.position,
        )
        # logger.debug("Reg 111-120 done")

        # yield from bps.mv(
        #     # Reg 123-127 in order
        #     dm_pars.I0mon, I0Mon.get(),
        #     dm_pars.burst_mode_state, 0,   # 0 for Lambda, other detector might use this
        #     dm_pars.number_of_bursts, 0,   # 0 for Lambda, other detector might use this
        #     dm_pars.first_usable_burst, 0,   # 0 for Lambda, other detector might use this
        #     dm_pars.last_usable_burst, 0,   # 0 for Lambda, other detector might use this
        # )
        # # logger.debug("Reg 123-127 done")

        try:
            yield from bps.mv(
                # Reg 123-127 in order
                dm_pars.I0mon, I0Mon.get(),
                dm_pars.burst_mode_state, 0,   # 0 for Lambda, other detector might use this
                dm_pars.number_of_bursts, 0,   # 0 for Lambda, other detector might use this
                dm_pars.first_usable_burst, 0,   # 0 for Lambda, other detector might use this
                dm_pars.last_usable_burst, 0,   # 0 for Lambda, other detector might use this
            )
        except ophyd.signal.ReadTimeoutError as exc:
            logger.warn("EPICS ReadTimeoutError from scaler (ignoring): %s", str(exc))


    def update_metadata_postscan():
        # since we inherited ALL the user's namespace, we have RE and db
        scan_id = RE.md["scan_id"]
        uid = db[-1].start["uid"]
        yield from bps.mv(
            # source end values
            dm_pars.source_end_datetime, timestamp_now(),
            dm_pars.source_end_current, aps.current.get(),
            dm_pars.uid, uid,
            dm_pars.scan_id, int(scan_id),
            dm_pars.datafilename, areadet.plugin_file_name,
        )
        # logger.debug("dm_pars.datafilename")

    def inner_count(devices, md={}):
        yield from bps.open_run(md=md)
        for obj in devices:
            yield from bps.stage(obj)
        grp = bps._short_uid('trigger')
        no_wait = True
        for obj in devices:
            if hasattr(obj, 'trigger'):
                no_wait = False
                yield from bps.trigger(obj, group=grp)
        if areadet.cam.EXT_TRIGGER > 0:
            yield from soft_glue.start_trigger()
        # Skip 'wait' if none of the devices implemented a trigger method.
        if not no_wait:
            yield from bps.wait(group=grp)
        yield from bps.create('primary')
        # ret = {}  # collect and return readings to give plan access to them
        for obj in devices:
            reading = (yield from bps.read(obj))
            # if reading is not None:
            #     ret.update(reading)
        yield from bps.save()
        for obj in devices:
            yield from bps.unstage(obj)
        yield from bps.close_run()
        # return ret

    # @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def full_acquire_procedure(md={}):
        logger.debug("before update_metadata_prescan()")
        yield from update_metadata_prescan()
        logger.debug("after update_metadata_prescan()")

        logger.debug("supplied metadata = %s", md)
        logger.debug("file_name = %s", file_name)
        logger.debug("file_path = %s", file_path)
        _md = {
            "file_name": file_name,
            "file_path": str(file_path)
        }
        _md.update(md)
        logger.debug("metadata = %s", _md)
        # start autocount on the scaler
        # yield from bps.mv(scaler1.count, "Count")
        # print(f"DIAGNOSTIC ({__name__},full_acquire_procedure): scaler1.stage_sigs={scaler1.stage_sigs}")
        # print(f"DIAGNOSTIC ({__name__},full_acquire_procedure): scaler1._staged={scaler1._staged}")
        # print(f"DIAGNOSTIC ({__name__},full_acquire_procedure): scaler1.count={scaler1.count}")
        # print(f"DIAGNOSTIC ({__name__},full_acquire_procedure): scaler1.count_mode={scaler1.count_mode}")
        # logger.info("scaler should be autocounting now")

        # do the acquisition (the scan)
        logger.debug("before count()")
        # yield from bp.count([areadet], md=md)
        yield from inner_count([areadet], md=_md)
        logger.debug("after count()")

        yield from update_metadata_postscan()
        hdf_with_fullpath = make_hdf5_workflow_filename()
        print(f"HDF5 workflow file name: {hdf_with_fullpath}")

        if not hdf_with_fullpath.parent.exists():
            hdf_with_fullpath.parent.mkdir(parents=True)

        dm_workflow.create_hdf5_file(str(hdf_with_fullpath))

        # update these str values from the string registers
        dm_workflow.transfer = dm_pars.transfer.get()
        dm_workflow.analysis = dm_pars.analysis.get()

        # no need to yield from since the function is not a plan
        kickoff_DM_workflow(str(hdf_with_fullpath), analysis=submit_xpcs_job)

    @apstools.utils.run_in_thread
    def kickoff_DM_workflow(hdf_workflow_file, analysis=True):
        logger.info(f"DM workflow kickoff starting: analysis:{analysis}  file:{hdf_workflow_file}")
        if analysis:
            out, err = dm_workflow.DataAnalysis(hdf_workflow_file)
        else:
            out, err = dm_workflow.DataTransfer(hdf_workflow_file)
        logger.info("DM workflow kickoff done")
        logger.info(out)
        if len(err) > 0:
            logger.error(err)

    logger.info("calling full_acquire_procedure()")
    return (yield from full_acquire_procedure(md=md))
