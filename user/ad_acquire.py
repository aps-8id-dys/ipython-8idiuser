# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)


"""
bluesky data acquisition plans
"""

def AD_Acquire(areadet, 
        acquire_time=0.1, acquire_period=0.11, 
        num_images=100, file_name="A001",
        submit_xpcs_job=True,
        atten=None, path=None):
    """
    acquisition sequence initiating data management workflow

    outline of acquisition sequence:

    * define cam params such as acquire time, period, 
      num images, camera mode
    * define file plugin immout params such as file path,
      file name, num_images, file_number, capture
    * configure scaler channels for monitoring some 
      scalers and devices such as temperature
    * trigger area detector while monitoring the 
      above params
    """
    logger.info("AD_Acquire starting")
    path = path or f"/home/8-id-i/{aps_cycle}/jemian_201908"
    file_path = os.path.join(path,file_name)
    if not file_path.endswith(os.path.sep):
        file_path += os.path.sep
    logger.info(f"file_path = {file_path}")
    
    atten = atten or Atten1
    assert atten in (Atten1, Atten2)

    # select the detector's number
    yield from bps.mv(dm_pars.detNum, areadet.detector_number)

    yield from areadet.cam.setup_modes(num_images)

    # Ask the devices to configure themselves for this plan.
    # no need to yield here, method does not have "yield from " calls
    scaler1.staging_setup_DM(acquire_period)
    areadet.staging_setup_DM(file_path, file_name,
            num_images, acquire_time, acquire_period)
    dm_workflow.set_xpcs_qmap_file(areadet.qmap_file)

    scaler1.select_channels(None) 
    monitored_things = [
        #scaler1.channels.chan01,
        #scaler1.channels.chan02,
        #scaler1.channels.chan03,
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
        if path.startswith("/data"):
            path = os.path.join("/", "home", "8-id-i", *path.split("/")[2:])
            logger.debug(f"modified path: {path}")
            if not os.path.exists(path):
                os.makedirs(path)
                logger.debug(f"created path: {path}")
        fname = (
            f"{file_name}"
            f"_{dm_pars.data_begin.value:04.0f}"
            f"-{dm_pars.data_end.value:04.0f}"
        )
        fullname = dm_workflow.cleanupFilename(
            os.path.join(path, f"{fname}.hdf"))
        suffix = 0
        while os.path.exists(fullname):
            suffix += 1
            fullname = os.path.join(path, f"{fname}__{suffix:03d}.hdf")
        if suffix > 0:
            logger.info(f"using modified file name: {fullname}")
        return fullname

    def update_metadata_prescan():
        detNum = int(dm_pars.detNum.value)
        det_pars = dm_workflow.detectors.getDetectorByNumber(detNum)
        logger.info(f"detNum={detNum}, det_pars={det_pars}")
        yield from bps.mv(
            # StrReg 2-7 in order
            dm_pars.root_folder, file_path,
        )
        logger.info("dm_pars.root_folder")

        yield from bps.mv(
            dm_pars.user_data_folder, os.path.dirname(file_path),   # just last item in path
        )
        logger.info("dm_pars.user_data_folder")

        yield from bps.mv(
            dm_pars.data_folder, file_name,
        )
        logger.info("dm_pars.data_folder")

        yield from bps.mv(
            dm_pars.datafilename, areadet.plugin_file_name,
        )
        logger.info("dm_pars.datafilename")

        yield from bps.mv(
            dm_pars.source_begin_datetime, timestamp_now(),
        )
        logger.info("dm_pars.source_begin_datetime")

        yield from bps.mv(
            # Reg 121
            dm_pars.source_begin_current, aps.current.value,
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
            dm_pars.attenuation, atten.value,
        )
        logger.info("Reg 121, 101-110 done")

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
        logger.info("Reg 111-120 done")

        yield from bps.mv(
            # Reg 123-127 in order
            dm_pars.I0mon, I0Mon.value,
            dm_pars.burst_mode_state, 0,   # 0 for Lambda, other detector might use this
            dm_pars.number_of_bursts, 0,   # 0 for Lambda, other detector might use this
            dm_pars.first_usable_burst, 0,   # 0 for Lambda, other detector might use this
            dm_pars.last_usable_burst, 0,   # 0 for Lambda, other detector might use this
        )
        logger.info("Reg 123-127 done")

    def update_metadata_postscan():
        # since we inherited ALL the user's namespace, we have RE and db
        scan_id = RE.md["scan_id"]
        uid = db[-1].start["uid"]
        yield from bps.mv(
            # source end values
            dm_pars.source_end_datetime, timestamp_now(),
            dm_pars.source_end_current, aps.current.value,
            dm_pars.uid, db[-1].start["uid"],
            dm_pars.scan_id, int(RE.md["scan_id"]),
        )

    def inner_count(devices, md={}):
        yield from bps.open_run(md=md)
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
        yield from bps.close_run()
        # return ret

    @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def full_acquire_procedure():
        logger.info("before update_metadata_prescan()")
        yield from update_metadata_prescan()
        logger.info("after update_metadata_prescan()")

        md = {
            "file_name": file_name,
            "file_path": file_path
        }
        # start autocount on the scaler
        yield from bps.mv(scaler1.count, "Count")
        logger.info("scaler should be autocounting now")

        # do the acquisition (the scan)
        logger.info("before count()")
        # yield from bp.count([areadet], md=md)
        yield from inner_count([areadet], md=md)
        logger.info("after count()")

        yield from update_metadata_postscan()
        hdf_with_fullpath = make_hdf5_workflow_filename()
        print(f"YO! {hdf_with_fullpath}")

        dm_workflow.create_hdf5_file(hdf_with_fullpath)
        
        # update these str values from the string registers
        dm_workflow.transfer = dm_pars.transfer.value
        dm_workflow.analysis = dm_pars.analysis.value

        # no need to yield from since the function is not a plan
        kickoff_DM_workflow(hdf_with_fullpath, analysis=submit_xpcs_job)

    @APS_utils.run_in_thread
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
    return (yield from full_acquire_procedure())
