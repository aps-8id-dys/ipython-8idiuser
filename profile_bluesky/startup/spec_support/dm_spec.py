
"""
APS Data Management workflow support for SPEC
"""

import datetime
import epics

from . import APS_DM_8IDI


class DataManagementMetadata:
    """
    signals for the APS Data Management service
    """
    angle = epics.PV("8idi:Reg19")
    attenuation = epics.PV("8idi:Reg110")
    beam_center_x = epics.PV("8idi:Reg11")
    beam_center_y = epics.PV("8idi:Reg12")
    # beam_size_H : see si2.hgap.value
    # beam_size_V : see si2.vgap.value
    burst_mode_state = epics.PV("8idi:Reg124")
    ccdxspec = epics.PV("8idi:Reg18")
    ccdzspec = epics.PV("8idi:Reg17")
    cols = epics.PV("8idi:Reg105")
    compression = epics.PV("8idi:Reg8")
    dark_begin = epics.PV("8idi:Reg111")
    dark_end = epics.PV("8idi:Reg112")
    data_begin = epics.PV("8idi:Reg113")
    data_end = epics.PV("8idi:Reg114")
    datafilename = epics.PV("8idi:StrReg5", string=True)
    data_folder = epics.PV("8idi:StrReg4", string=True)
    detector_distance = epics.PV("8idi:Reg5")
    detNum = epics.PV("8idi:Reg2")
    exposure_period = epics.PV("8idi:Reg116")
    exposure_time = epics.PV("8idi:Reg115")
    first_usable_burst = epics.PV("8idi:Reg126")
    geometry_num = epics.PV("8idi:Reg3")
    hdf_metadata_version = epics.PV("8idi:Reg1")
    I0mon = epics.PV("8idi:Reg123")
    kinetics_state = epics.PV("8idi:Reg107")
    kinetics_top = epics.PV("8idi:Reg109")
    kinetics_window_size = epics.PV("8idi:Reg108")
    last_usable_burst = epics.PV("8idi:Reg127")
    number_of_bursts = epics.PV("8idi:Reg125")
    ## pid1 = epics.PV("8idi:pid1.VAL")
    roi_x1 = epics.PV("8idi:Reg101")
    roi_x2 = epics.PV("8idi:Reg102")
    roi_y1 = epics.PV("8idi:Reg103")
    roi_y2 = epics.PV("8idi:Reg104")
    root_folder = epics.PV("8idi:StrReg2", string=True)
    rows = epics.PV("8idi:Reg106")
    # sample_pitch : see samplestage.theta
    # sample_roll : see samplestage.chi
    # sample_yaw : see samplestage.phi
    source_begin_beam_intensity_incident = epics.PV("8idi:Reg9")
    source_begin_beam_intensity_transmitted = epics.PV("8idi:Reg10")
    source_begin_current = epics.PV("8idi:Reg121")
    source_begin_datetime = epics.PV("8idi:StrReg6", string=True)
    # source_begin_energy : see monochromator.energy.value
    source_end_current = epics.PV("8idi:Reg122")
    source_end_datetime = epics.PV("8idi:StrReg7", string=True)
    specfile = epics.PV("8idi:StrReg1", string=True)
    specscan_dark_number = epics.PV("8idi:Reg117")
    specscan_data_number = epics.PV("8idi:Reg118")
    stage_x = epics.PV("8idi:Reg119")
    stage_z = epics.PV("8idi:Reg120")
    stage_zero_x = epics.PV("8idi:Reg13")
    stage_zero_z = epics.PV("8idi:Reg14")

    # temperature_A  : see lakeshore.loop1.temperature
    # temperature_A_set : see lakeshore.loop1.target
    # temperature_B : see lakeshore.loop2.temperature
    # temperature_B_set  : see lakeshore.loop2.target

    # translation_table_x : see samplestage.table.x
    # translation_table_y = epics.PV("8idi:TI3:z.VAL")    # TODO: defined elsewhere?
    # translation_table_z = epics.PV("8idi:TI3:y.VAL")    # TODO: defined elsewhere?
    # translation_x = epics.PV("8idi:m54.RBV")            # TODO: defined elsewhere?
    # translation_y = epics.PV("8idi:m49.RBV")            # TODO: defined elsewhere?
    # translation_z = epics.PV("8idi:m50.RBV")            # TODO: defined elsewhere?
    user_data_folder = epics.PV("8idi:StrReg3", string=True)
    xspec = epics.PV("8idi:Reg15")
    zspec = epics.PV("8idi:Reg16")


# What APS run cycle are we in?  Hackulate it.
dt = datetime.datetime.now()
aps_cycle = f"{dt.year}-{int((dt.month-0.1)/4) + 1}"

xpcs_qmap_file = "Lambda_qmap.h5"		# TODO:

dm_pars = DataManagementMetadata(name="dm_pars")
dm_workflow = APS_DM_8IDI.DM_Workflow(dm_pars, aps_cycle, xpcs_qmap_file)