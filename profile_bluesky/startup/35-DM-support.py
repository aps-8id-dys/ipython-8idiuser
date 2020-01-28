logger.info(__file__)

"""
support for APS data management
"""

from spec_support import APS_DM_8IDI


class DataManagementMetadata(Device):
    """
    signals for the APS Data Management service
    """
    airgap = Component(EpicsSignal, "8idi:Reg4")
    angle = Component(EpicsSignal, "8idi:Reg19")
    ARun_number = Component(EpicsSignal, "8idi:Reg173")
    attenuation = Component(EpicsSignal, "8idi:Reg110")
    beam_center_x = Component(EpicsSignal, "8idi:Reg11")
    beam_center_y = Component(EpicsSignal, "8idi:Reg12")
    beam_size_H = Component(EpicsSignal, "8idi:Reg151")
    beam_size_V = Component(EpicsSignal, "8idi:Reg152")
    burst_mode_state = Component(EpicsSignal, "8idi:Reg124")
    ccdx0 = Component(EpicsSignal, "8idi:Reg13")
    ccdz0 = Component(EpicsSignal, "8idi:Reg14")
    ccdxspec = Component(EpicsSignal, "8idi:Reg17")
    ccdzspec = Component(EpicsSignal, "8idi:Reg18")
    cols = Component(EpicsSignal, "8idi:Reg105")
    compression = Component(EpicsSignal, "8idi:Reg8")
    dark_begin = Component(EpicsSignal, "8idi:Reg111")
    dark_end = Component(EpicsSignal, "8idi:Reg112")
    data_begin = Component(EpicsSignal, "8idi:Reg113")
    data_end = Component(EpicsSignal, "8idi:Reg114")
    datafilename = Component(EpicsSignal, "8idi:StrReg5", string=True)
    data_folder = Component(EpicsSignal, "8idi:StrReg4", string=True)
    data_subfolder = Component(EpicsSignal, "8idi:StrReg10", string=True)
    detector_distance = Component(EpicsSignal, "8idi:Reg5")
    detNum = Component(EpicsSignal, "8idi:Reg2")
    exposure_period = Component(EpicsSignal, "8idi:Reg116")
    exposure_time = Component(EpicsSignal, "8idi:Reg115")
    first_usable_burst = Component(EpicsSignal, "8idi:Reg126")
    geometry_num = Component(EpicsSignal, "8idi:Reg3")
    hdf_metadata_version = Component(EpicsSignal, "8idi:Reg1")
    I0mon = Component(EpicsSignal, "8idi:Reg123")
    kinetics_state = Component(EpicsSignal, "8idi:Reg107")
    kinetics_top = Component(EpicsSignal, "8idi:Reg109")
    kinetics_window_size = Component(EpicsSignal, "8idi:Reg108")
    last_usable_burst = Component(EpicsSignal, "8idi:Reg127")
    number_of_bursts = Component(EpicsSignal, "8idi:Reg125")
    ## pid1 = Component(EpicsSignal, "8idi:pid1.VAL")
    pid1_set = Component(EpicsSignal, "8idi:Reg167")
    pid2_set = Component(EpicsSignal, "8idi:Reg168")
    qmap_file = Component(EpicsSignal, "8idi:StrReg13", string=True)
    roi_x1 = Component(EpicsSignal, "8idi:Reg101")
    roi_x2 = Component(EpicsSignal, "8idi:Reg102")
    roi_y1 = Component(EpicsSignal, "8idi:Reg103")
    roi_y2 = Component(EpicsSignal, "8idi:Reg104")
    root_folder = Component(EpicsSignal, "8idi:StrReg2", string=True)
    rows = Component(EpicsSignal, "8idi:Reg106")
    sample_pitch = Component(EpicsSignal, "8idi:Reg164")
    sample_roll = Component(EpicsSignal, "8idi:Reg165")
    sample_yaw = Component(EpicsSignal, "8idi:Reg166")
    scan_id = Component(EpicsSignal, "8idi:Reg169")
    source_begin_beam_intensity_incident = Component(EpicsSignal, "8idi:Reg9")
    source_begin_beam_intensity_transmitted = Component(EpicsSignal, "8idi:Reg10")
    source_begin_current = Component(EpicsSignal, "8idi:Reg121")
    source_begin_datetime = Component(EpicsSignal, "8idi:StrReg6", string=True)
    source_begin_energy = Component(EpicsSignal, "8idi:Reg153")
    source_end_current = Component(EpicsSignal, "8idi:Reg122")
    source_end_datetime = Component(EpicsSignal, "8idi:StrReg7", string=True)
    specfile = Component(EpicsSignal, "8idi:StrReg1", string=True)
    specscan_dark_number = Component(EpicsSignal, "8idi:Reg117")
    specscan_data_number = Component(EpicsSignal, "8idi:Reg118")
    stage_x = Component(EpicsSignal, "8idi:Reg119")
    stage_z = Component(EpicsSignal, "8idi:Reg120")
    stage_zero_x = Component(EpicsSignal, "8idi:Reg13")
    stage_zero_z = Component(EpicsSignal, "8idi:Reg14")
    stop_before_next_scan = Component(EpicsSignal, "8idi:Reg174")

    temperature_A = Component(EpicsSignal, "8idi:Reg154")
    temperature_B = Component(EpicsSignal, "8idi:Reg155")
    temperature_A_set = Component(EpicsSignal, "8idi:Reg156")
    temperature_B_set = Component(EpicsSignal, "8idi:Reg157")

    translation_table_x = Component(EpicsSignal, "8idi:Reg161")
    translation_table_y = Component(EpicsSignal, "8idi:Reg162")
    translation_table_z = Component(EpicsSignal, "8idi:Reg163")

    translation_x = Component(EpicsSignal, "8idi:Reg158")
    translation_y = Component(EpicsSignal, "8idi:Reg159")
    translation_z = Component(EpicsSignal, "8idi:Reg160")

    transfer = Component(EpicsSignal, "8idi:StrReg15", string=True)
    analysis = Component(EpicsSignal, "8idi:StrReg16", string=True)

    uid = Component(EpicsSignal, "8idi:StrReg11", string=True)
    user_data_folder = Component(EpicsSignal, "8idi:StrReg3", string=True)
    xspec = Component(EpicsSignal, "8idi:Reg15")
    zspec = Component(EpicsSignal, "8idi:Reg16")


# What APS run cycle are we in?  Hackulate it.
dt = datetime.datetime.now()
aps_cycle = f"{dt.year}-{int((dt.month-0.1)/4) + 1}"

xpcs_qmap_file = "Lambda_qmap.h5"		# dm_workflow.set_xpcs_qmap_file("new_name.h5")

dm_pars = DataManagementMetadata(name="dm_pars")
dm_workflow = APS_DM_8IDI.DM_Workflow(
    dm_pars, aps_cycle, xpcs_qmap_file,
    transfer=dm_pars.transfer.value,
    analysis=dm_pars.analysis.value,
    )
