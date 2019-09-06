logger.info(__file__)

"""
support for APS data management
"""

from spec_support import APS_DM_8IDI


class DataManagementMetadata(Device):
    """
    signals for the APS Data Management service
    """
    angle = EpicsSignal("8idi:Reg19")
    attenuation = EpicsSignal("8idi:Reg110")
    beam_center_x = EpicsSignal("8idi:Reg11")
    beam_center_y = EpicsSignal("8idi:Reg12")
    beam_size_H = EpicsSignal("8idi:Slit2Hsize.VAL")    # TODO: defined elsewhere?
    beam_size_V = EpicsSignal("8idi:Slit3Vsize.VAL")    # TODO: defined elsewhere?
    burst_mode_state = EpicsSignal("8idi:Reg124")
    ccdxspec = EpicsSignal("8idi:Reg18")
    ccdzspec = EpicsSignal("8idi:Reg17")
    cols = EpicsSignal("8idi:Reg105")
    compression = EpicsSignal("8idi:Reg8")
    dark_begin = EpicsSignal("8idi:Reg111")
    dark_end = EpicsSignal("8idi:Reg112")
    data_begin = EpicsSignal("8idi:Reg113")
    data_end = EpicsSignal("8idi:Reg114")
    datafilename = EpicsSignal("8idi:StrReg5", string=True)
    data_folder = EpicsSignal("8idi:StrReg4", string=True)
    detector_distance = EpicsSignal("8idi:Reg5")
    detNum = EpicsSignal("8idi:Reg2")
    exposure_period = EpicsSignal("8idi:Reg116")
    exposure_time = EpicsSignal("8idi:Reg115")
    first_usable_burst = EpicsSignal("8idi:Reg126")
    geometry_num = EpicsSignal("8idi:Reg3")
    hdf_metadata_version = EpicsSignal("8idi:Reg1")
    I0mon = EpicsSignal("8idi:Reg123")
    kinetics_state = EpicsSignal("8idi:Reg107")
    kinetics_top = EpicsSignal("8idi:Reg109")
    kinetics_window_size = EpicsSignal("8idi:Reg108")
    last_usable_burst = EpicsSignal("8idi:Reg127")
    number_of_bursts = EpicsSignal("8idi:Reg125")
    ## pid1 = EpicsSignal("8idi:pid1.VAL")
    roi_x1 = EpicsSignal("8idi:Reg101")
    roi_x2 = EpicsSignal("8idi:Reg102")
    roi_y1 = EpicsSignal("8idi:Reg103")
    roi_y2 = EpicsSignal("8idi:Reg104")
    root_folder = EpicsSignal("8idi:StrReg2", string=True)
    rows = EpicsSignal("8idi:Reg106")
    sample_pitch = EpicsSignal("8idi:m52.RBV")             # TODO: defined elsewhere?
    sample_roll = EpicsSignal("8idi:m53.RBV")              # TODO: defined elsewhere?
    sample_yaw = EpicsSignal("8idi:m51.RBV")               # TODO: defined elsewhere?
    source_begin_beam_intensity_incident = EpicsSignal("8idi:Reg9")
    source_begin_beam_intensity_transmitted = EpicsSignal("8idi:Reg10")
    source_begin_current = EpicsSignal("8idi:Reg121")
    source_begin_datetime = EpicsSignal("8idi:StrReg6", string=True)
    source_begin_energy = EpicsSignal("8idimono:sm2.RBV")    # TODO: defined elsewhere?
    source_end_current = EpicsSignal("8idi:Reg122")
    source_end_datetime = EpicsSignal("8idi:StrReg7", string=True)
    specfile = EpicsSignal("8idi:StrReg1", string=True)
    specscan_dark_number = EpicsSignal("8idi:Reg117")
    specscan_data_number = EpicsSignal("8idi:Reg118")
    stage_x = EpicsSignal("8idi:Reg119")
    stage_z = EpicsSignal("8idi:Reg120")
    stage_zero_x = EpicsSignal("8idi:Reg13")
    stage_zero_z = EpicsSignal("8idi:Reg14")
    temperature_A = EpicsSignal("8idi:LS336:TC4:IN1")    # TODO: defined elsewhere?
    temperature_A_set = EpicsSignal("8idi:LS336:TC4:OUT1:SP")    # TODO: defined elsewhere?
    temperature_B = EpicsSignal("8idi:LS336:TC4:IN1")    # TODO: defined elsewhere?
    temperature_B_set = EpicsSignal("8idi:LS336:TC4:OUT1:SP")    # TODO: defined elsewhere?
    translation_table_x = EpicsSignal("8idi:TI3:x.VAL")    # TODO: defined elsewhere?
    translation_table_y = EpicsSignal("8idi:TI3:z.VAL")    # TODO: defined elsewhere?
    translation_table_z = EpicsSignal("8idi:TI3:y.VAL")    # TODO: defined elsewhere?
    translation_x = EpicsSignal("8idi:m54.RBV")            # TODO: defined elsewhere?
    translation_y = EpicsSignal("8idi:m49.RBV")            # TODO: defined elsewhere?
    translation_z = EpicsSignal("8idi:m50.RBV")            # TODO: defined elsewhere?
    user_data_folder = EpicsSignal("8idi:StrReg3", string=True)
    xspec = EpicsSignal("8idi:Reg15")
    zspec = EpicsSignal("8idi:Reg16")


dm_pars = DataManagementMetadata(name="dm_pars")
dm_workflow = APS_DM_8IDI.DM_Workflow(dm_pars)
