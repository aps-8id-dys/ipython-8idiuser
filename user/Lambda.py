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
        submit_xpcs_job=True):
    path = "/home/8-id-i/2019-2/jemian_201908"
    file_path = os.path.join(path,file_name)
    if not file_path.endswith(os.path.sep):
        file_path += os.path.sep
    
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
            file_name
            f"_{dm_pars.data_begin.value:04d}"
            f"_{dm_pars.data_end.value:04d}"
        )
        fullname = os.path.join(path, f"{fname}.hdf")
        suffix = 0
        while os.path.exists(fullname):
            suffix += 1
            fullname = os.path.join(path, f"{fname}__{suffix:03d}.hdf")
        if suffix > 0:
            print(f"using modified file name: {fullname}")  # TODO: use logging
        return fullname

    def prescan_update_metadata():
        det_pars = dm_workflow.detectors.masterDict[dm_pars.detNum]
        yield from bps.mv(      # TODO: verify all this
            dm_pars.root_folder, file_path,
            dm_pars.parent_folder, os.path.dirname(file_path),
            dm_pars.data_folder, file_name,
            dm_pars.datafilename, areadet.get_plugin_file_name(),
            # source begin values
            dm_pars.source_begin_datetime, str(datetime.datetime.now()),  # TODO: format?
            dm_pars.source_begin_current, aps.current.value,
            # parameters from detector database, Reg 101-110 in order
            dm_pars.roi_x1, 0,
            dm_pars.roi_x2, det_pars.ccdHardwareColSize-1,
            dm_pars.roi_y1, 0,
            dm_pars.roi_y2, det_pars.ccdHardwareRowSize-1,
            dm_pars.cols, det_pars.ccdHardwareColSize,
            dm_pars.rows, det_pars.ccdHardwareRowSize,
            dm_pars.kinetics_state, 0,  # FIXME:
            dm_pars.kinetics_window_size, 0,    # FIXME:
            dm_pars.kinetics_top, 0,    # FIXME:
            dm_pars.attenuation, Atten1.value,  # TODO: verify
            # image parameters: Reg 111-120 in order
            dm_pars.dark_begin, -1, # TODO: verify
            dm_pars.dark_end, -1,   # TODO: verify
            dm_pars.data_begin, 1,
            dm_pars.data_end, num_images,
            dm_pars.exposure_time, acquire_time,
            dm_pars.exposure_period, acquire_period,
            dm_pars.specscan_dark_number, -1,   # TODO: verify
            dm_pars.specscan_data_number, 680,  # TODO: verify
            dm_pars.stage_x, det_pars.dpix * det_pars.ccdHardwareColSize,   # TODO: verify
            dm_pars.stage_z, det_pars.dpix * det_pars.ccdHardwareRowSize,   # TODO: verify
            # TODO: what else?
            # TODO: StrReg 1-10 in order
            # TODO: Reg 121-130 in order
        )

    def postscan_update_metadata():
        yield from bps.mv(
            # source end values
            dm_pars.source_end_datetime, str(datetime.datetime.now()),  # TODO: format?
            dm_pars.source_end_current, aps.current.value,
            # TODO: what else?
        )

    @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def inner():
        # write pre-acquisition metadata to the dm_pars
        yield from prescan_update_metadata()

        md = {
            "file_name": file_name,
            "file_path": file_path
        }
        # do the scan
        yield from bps.mv(scaler1.count, "Count")
        yield from bp.count([areadet], md=md)

        # write post-acquisition metadata to the dm_pars
        yield from postscan_update_metadata()
        hdf_with_fullpath = make_hdf5_workflow_filename()
        yield from dm_workflow.create_hdf5_file(hdf_with_fullpath, as_bluesky_plan=True)
        
        kickoff_DM_workflow(hdf_with_fullpath, analysis=submit_xpcs_job)

    @APS_utils.run_in_thread
    def kickoff_DM_workflow(hdf_workflow_file, analysis=True):
        # TODO: logging before starting workflow
        if analysis:
            out, err = dm_workflow.DataAnalysis(hdf_workflow_file)
        else:
            out, err = dm_workflow.DataTransfer(hdf_workflow_file)
        # TODO: log out & err after workflow finishes

    return (yield from inner())
