# logger.info(__file__)

"""
support for APS data management
"""

import datetime
import epics
import pyRestTable

from . import APS_DM_8IDI


class MyPV(object):
    """
    wrapper so we can read waveform strings as strings
    """
    def __init__(self, pv, string=False):
        self.string = string
        self.pv = epics.PV(pv)
        self.description = epics.PV(pv + ".DESC")
        self.data_type = {
            True: "text", 
            False: "number"
            }[pv.find(":StrReg") > 0]
        p = pv.find("Reg")
        n = int(pv[p+3:])
        self.id_str = "%s_%03d" % (self.data_type, n)
    
    def __repr__(self):
        args = '"%s"' % self.pv.pvname
        if self.string:
            args += ", string=True"
        return 'MyPV(%s)' % args

    @property
    def value(self):
        return self.pv.get(as_string=self.string)


class DMDBase(object):

    @property
    def pv_attributes(self):
        items = self.__dir__()
        attrs = []
        for k in items:
            if k.startswith("_") or k in ('pv_attributes', 'getTable'):
                continue
            obj = getattr(self, k)
            if isinstance(obj, MyPV):
                attrs.append(k)
        return attrs

    def getTable(self):
        tbl = pyRestTable.Table()
        tbl.labels = "type name PV description value".split()

        def sorter(key):
            obj = getattr(self, key)
            return obj.id_str

        for k in sorted(self.pv_attributes, key=sorter):
            obj = getattr(self, k)
            tbl.addRow(
                [
                    obj.data_type,
                    k,
                    obj.pv.pvname,
                    obj.description.value,
                    obj.value,
                ]
            )
        return tbl


class DataManagementMetadata(DMDBase):
    """
    signals for the APS Data Management service
    """
    angle = MyPV("8idi:Reg19")
    attenuation = MyPV("8idi:Reg110")
    beam_center_x = MyPV("8idi:Reg11")
    beam_center_y = MyPV("8idi:Reg12")
    beam_size_H = MyPV("8idi:Reg151")
    beam_size_V = MyPV("8idi:Reg152")
    burst_mode_state = MyPV("8idi:Reg124")
    ccdxspec = MyPV("8idi:Reg18")
    ccdzspec = MyPV("8idi:Reg17")
    cols = MyPV("8idi:Reg105")
    compression = MyPV("8idi:Reg8")
    dark_begin = MyPV("8idi:Reg111")
    dark_end = MyPV("8idi:Reg112")
    data_begin = MyPV("8idi:Reg113")
    data_end = MyPV("8idi:Reg114")
    datafilename = MyPV("8idi:StrReg5", string=True)
    data_folder = MyPV("8idi:StrReg4", string=True)
    data_subfolder = MyPV("8idi:StrReg10", string=True)
    detector_distance = MyPV("8idi:Reg5")
    detNum = MyPV("8idi:Reg2")
    exposure_period = MyPV("8idi:Reg116")
    exposure_time = MyPV("8idi:Reg115")
    first_usable_burst = MyPV("8idi:Reg126")
    geometry_num = MyPV("8idi:Reg3")
    hdf_metadata_version = MyPV("8idi:Reg1")
    I0mon = MyPV("8idi:Reg123")
    kinetics_state = MyPV("8idi:Reg107")
    kinetics_top = MyPV("8idi:Reg109")
    kinetics_window_size = MyPV("8idi:Reg108")
    last_usable_burst = MyPV("8idi:Reg127")
    number_of_bursts = MyPV("8idi:Reg125")
    ## pid1 = MyPV("8idi:pid1.VAL")
    pid1_set = MyPV("8idi:Reg167")
    pid2_set = MyPV("8idi:Reg168")
    roi_x1 = MyPV("8idi:Reg101")
    roi_x2 = MyPV("8idi:Reg102")
    roi_y1 = MyPV("8idi:Reg103")
    roi_y2 = MyPV("8idi:Reg104")
    root_folder = MyPV("8idi:StrReg2", string=True)
    rows = MyPV("8idi:Reg106")
    sample_pitch = MyPV("8idi:Reg164")
    sample_roll = MyPV("8idi:Reg165")
    sample_yaw = MyPV("8idi:Reg166")
    scan_id = MyPV("8idi:Reg169", string=True)
    source_begin_beam_intensity_incident = MyPV("8idi:Reg9")
    source_begin_beam_intensity_transmitted = MyPV("8idi:Reg10")
    source_begin_current = MyPV("8idi:Reg121")
    source_begin_datetime = MyPV("8idi:StrReg6", string=True)
    source_begin_energy = MyPV("8idi:Reg153")
    source_end_current = MyPV("8idi:Reg122")
    source_end_datetime = MyPV("8idi:StrReg7", string=True)
    specfile = MyPV("8idi:StrReg1", string=True)
    specscan_dark_number = MyPV("8idi:Reg117")
    specscan_data_number = MyPV("8idi:Reg118")
    stage_x = MyPV("8idi:Reg119")
    stage_z = MyPV("8idi:Reg120")
    stage_zero_x = MyPV("8idi:Reg13")
    stage_zero_z = MyPV("8idi:Reg14")

    temperature_A = MyPV("8idi:Reg154")
    temperature_B = MyPV("8idi:Reg155")
    temperature_A_set = MyPV("8idi:Reg156")
    temperature_B_set = MyPV("8idi:Reg157")

    translation_table_x = MyPV("8idi:Reg161")
    translation_table_y = MyPV("8idi:Reg162")
    translation_table_z = MyPV("8idi:Reg163")

    translation_x = MyPV("8idi:Reg158")
    translation_y = MyPV("8idi:Reg159")
    translation_z = MyPV("8idi:Reg160")

    uid = MyPV("8idi:StrReg11", string=True)
    user_data_folder = MyPV("8idi:StrReg3", string=True)
    xspec = MyPV("8idi:Reg15")
    zspec = MyPV("8idi:Reg16")


# What APS run cycle are we in?  Hackulate it.
dt = datetime.datetime.now()
aps_cycle = f"{dt.year}-{int((dt.month-0.1)/4) + 1}"

xpcs_qmap_file = "Lambda_qmap.h5"		# workflow.set_xpcs_qmap_file("new_name.h5")

registers = DataManagementMetadata()
workflow = APS_DM_8IDI.DM_Workflow(registers, aps_cycle, xpcs_qmap_file)

# demo: print(registers.getTable())
