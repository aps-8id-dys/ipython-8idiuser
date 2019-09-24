# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)


"""
bluesky data acquisition plans
"""

AD_PATH_PREFIX = os.path.join("/data", aps_cycle)
BLUESKY_PATH_PREFIX = os.path.join("/home/8-id-i", aps_cycle)
AD_ACQUIRE_SUBPATH = "jemian_201908"


def AD_Acquire(areadet, 
        acquire_time=0.1, acquire_period=0.11, 
        num_images=100, file_name="A001",
        submit_xpcs_job=True,
        atten=None):
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
    file_subpath = AD_ACQUIRE_SUBPATH
    if not file_subpath.endswith(os.path.sep):
        file_subpath += os.path.sep
    
    bluesky_file_path = os.path.join(BLUESKY_PATH_PREFIX, file_subpath)
    ad_file_path = os.path.join(AD_PATH_PREFIX, file_subpath, file_name) + os.path.sep
    logger.info(f"bluesky_file_path = {bluesky_file_path}")
    logger.info(f"ad_file_path = {ad_file_path}")

    _p = os.path.join(bluesky_file_path, file_name)
    if not os.path.exists(_p):
        logger.info(f"creating directory {_p}")
        os.makedirs(_p)

    atten = atten or Atten1
    assert atten in (Atten1, Atten2)

    # Ask the devices to configure themselves for this plan.
    # no need to yield here, method does not have "yield from " calls
    scaler1.staging_setup_DM(acquire_period)
    areadet.staging_setup_DM(
        ad_file_path,
        file_name,
        num_images, 
        acquire_time, 
        acquire_period)
   
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

    def update_metadata_prescan():
        detNum = int(registers.detNum.value)
        det_pars = workflow.detectors.getDetectorByNumber(detNum)
        logger.info(f"detNum={detNum}, det_pars={det_pars}")
        yield from bps.mv(
            # StrReg 2-7 in order
            registers.root_folder, bluesky_file_path,
        )
        logger.debug("registers.root_folder")

        yield from bps.mv(
            registers.user_data_folder, os.path.dirname(bluesky_file_path),   # just last item in path
        )
        logger.debug("registers.user_data_folder")

        yield from bps.mv(
            registers.data_folder, file_name,
        )
        logger.debug("registers.data_folder")

        yield from bps.mv(
            registers.datafilename, areadet.plugin_file_name,
        )
        logger.debug("registers.datafilename")

        yield from bps.mv(
            registers.source_begin_datetime, timestamp_now(),
        )
        logger.debug("registers.source_begin_datetime")

        yield from bps.mv(
            # Reg 121
            registers.source_begin_current, aps.current.value,
            # Reg 101-110 in order
            registers.roi_x1, 0,
            registers.roi_x2, det_pars["ccdHardwareColSize"]-1,
            registers.roi_y1, 0,
            registers.roi_y2, det_pars["ccdHardwareRowSize"]-1,
            registers.cols, det_pars["ccdHardwareColSize"],
            registers.rows, det_pars["ccdHardwareRowSize"],
            registers.kinetics_state, 0,                  # FIXME: SPEC generated this
            registers.kinetics_window_size, 0,            # FIXME:
            registers.kinetics_top, 0,                    # FIXME:
            registers.attenuation, atten.value,
        )
        logger.debug("Reg 121, 101-110 done")

        yield from bps.mv(
            # Reg 111-120 in order
            #registers.dark_begin, -1,            #  edit if detector needs this
            #registers.dark_end, -1,              #  op cit
            registers.data_begin, 1,
            registers.data_end, num_images,
            registers.exposure_time, acquire_time,
            registers.exposure_period, acquire_period,
            # registers.specscan_dark_number, -1,   #  not used, detector takes no darks
            registers.stage_x, detu.x.position,
            registers.stage_z, detu.z.position,
        )
        logger.debug("Reg 111-120 done")

        yield from bps.mv(
            # Reg 123-127 in order
            registers.I0mon, I0Mon.value,
            registers.burst_mode_state, 0,   # 0 for Lambda, other detector might use this
            registers.number_of_bursts, 0,   # 0 for Lambda, other detector might use this
            registers.first_usable_burst, 0,   # 0 for Lambda, other detector might use this
            registers.last_usable_burst, 0,   # 0 for Lambda, other detector might use this
        )
        logger.debug("Reg 123-127 done")

    def update_metadata_postscan():
        # since we inherited ALL the user's namespace, we have RE and db
        scan_id = RE.md["scan_id"]
        uid = db[-1].start["uid"]
        yield from bps.mv(
            # source end values
            registers.source_end_datetime, timestamp_now(),
            registers.source_end_current, aps.current.value,
            registers.uid, db[-1].start["uid"],
            registers.scan_id, int(RE.md["scan_id"]),
        )

    @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def inner():
        logger.info("before update_metadata_prescan()")
        yield from update_metadata_prescan()
        logger.info("after update_metadata_prescan()")

        md = {
            "file_name": file_name,
            "file_path": bluesky_file_path
        }
        # start autocount on the scaler
        yield from bps.mv(scaler1.count, "Count")
        logger.info("scaler should be autocounting now")

        # do the acquisition (the scan)
        t0 = time.time()
        logger.debug("before count()")
        yield from bp.count([areadet], md=md)
        dt = time.time() - t0
        logger.debug(f"after count(), {dt:.3f}s")

        yield from update_metadata_postscan()

        t0 = time.time()
        logger.info("before starting data management workflow")
        yield from bps.mv(registers.workflow_caller, "bluesky")
        workflow.start_workflow(analysis=submit_xpcs_job)
        yield from bps.mv(registers.workflow_caller, "")
        dt = time.time() - t0
        logger.info(f"after starting data management workflow, {dt:.3f}s")

    logger.info("calling inner()")
    return (yield from inner())
