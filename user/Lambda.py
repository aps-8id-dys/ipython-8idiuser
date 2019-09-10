# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)


"""
define cam params such as acquire time, period, num images, camera mode
define file plugin immout params such as file path,file name, num_images, file_number, capture

configure scaler channels for monitoring some scalers and devices such as temperature

trigger area detector while monitoring the above params

"""

def AD_Acquire(areadet, 
        acquire_time=0.1, acquire_period=0.11, 
        num_images=100, file_name="A001",
        submit_xpcs_job=True,
        atten=None):
    path = "/home/8-id-i/2019-2/jemian_201908"
    file_path = os.path.join(path,file_name)
    if not file_path.endswith(os.path.sep):
        file_path += os.path.sep
    
    atten = atten or Atten1
    assert atten in (Atten1, Atten2)

    # Ask the devices to configure themselves for this plan.
    # no need to yield here, method does not have "yield from " calls
    scaler1.staging_setup_DM(acquire_period)
    areadet.staging_setup_DM(file_path, file_name,
            num_images, acquire_time, acquire_period)
   
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

    def make_hdf5_workflow_filename():
        path = os.path.join(file_path, data_folder) # TODO: verify
        if path.startswith("/data"):
            path = os.path.join("/", "home", "8-id-i", *path.split("/")[2:])
        fname = (
            f"_{file_name}"
            f"_{dm_pars.data_begin.value:04.0f}"
            f"-{dm_pars.data_end.value:04.0f}"
        )
        fullname = os.path.join(path, f"{fname}.hdf")
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
        yield from bps.mv(
            # StrReg 2-7 in order
            dm_pars.root_folder, file_path,
            dm_pars.user_data_folder, os.path.dirname(file_path),   # just last item in path
            dm_pars.data_folder, file_name,
            dm_pars.datafilename, areadet.plugin_file_name,
            dm_pars.source_begin_datetime, datetime.datetime.now().strftime("%c"),
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
            # Reg 123-127 in order
            dm_pars.I0mon, I0Mon.value,
            dm_pars.burst_mode_state, 0,   # 0 for Lambda, other detector might use this
            dm_pars.number_of_bursts, 0,   # 0 for Lambda, other detector might use this
            dm_pars.first_usable_burst, 0,   # 0 for Lambda, other detector might use this
            dm_pars.last_usable_burst, 0,   # 0 for Lambda, other detector might use this
        )

    def update_metadata_postscan():
        scan_id = 680   # TODO: get from RE.md["scan_id"] or equal
        yield from bps.mv(
            # source end values
            dm_pars.source_end_datetime, datetime.datetime.now().strftime("%c"),
            dm_pars.source_end_current, aps.current.value,
            # TODO: scan's uuid : we need a StrReg for this
        )

    @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def inner():
        yield from update_metadata_prescan()

        md = {
            "file_name": file_name,
            "file_path": file_path
        }
        # start autocount on the scaler
        yield from bps.mv(scaler1.count, "Count")
        # do the acquisition (the scan)
        yield from bp.count([areadet], md=md)

        yield from update_metadata_postscan()
        hdf_with_fullpath = make_hdf5_workflow_filename()

        yield from dm_workflow.create_hdf5_file(hdf_with_fullpath, as_bluesky_plan=True)
        
        # no need to yield from since the function is not a plan
        kickoff_DM_workflow(hdf_with_fullpath, analysis=submit_xpcs_job)

    @APS_utils.run_in_thread
    def kickoff_DM_workflow(hdf_workflow_file, analysis=True):
        logger.info(f"DM workflow starting: analysis:{analysis}  file:{hdf_workflow_file}")
        if analysis:
            out, err = dm_workflow.DataAnalysis(hdf_workflow_file)
        else:
            out, err = dm_workflow.DataTransfer(hdf_workflow_file)
        logger.info("DM workflow done")
        logger.info(out)
        if len(err) > 0:
            logger.error(err)

    return (yield from inner())
