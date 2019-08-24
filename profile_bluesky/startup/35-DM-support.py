logger.info(__file__)

"""
support for APS data management
"""

dm_signals = {}


class EpicsSignalDM(EpicsSignal):
    """custom class for Data Management metadata"""
    h5address = None
    
    # needs constructor to handle additional terms
    def __init__(self, 
                 prefix, h5address, *args, 
                 size = (1, 1),
                 dtype = None,
                 **kwargs):
        self.h5address = h5address
        self.size = size
        self.dtype = dtype
        super().__init__(prefix, *args, **kwargs)
        
        # keep our own dictionary of the DM metadata signals
        dm_signals[h5address] = self


class DataManagementMetadata(Device):
    """
    signals for the APS Data Management service
    
    The EpicsSignalDM signals will be written to the HDF5 file
    """
    # will not be stored in HDF5 file
    detNum = Component(EpicsSignal, "8idi:Reg2")
    geometry_num = Component(EpicsSignal, "8idi:Reg3")
    kinetics_state = Component(EpicsSignal, "8idi:Reg107")
    burst_mode_state = Component(EpicsSignal, "8idi:Reg124")
    compression = Component(EpicsSignal, "8idi:Reg8")       # , string=True

    hdf_metadata_version = Component(EpicsSignalDM, "8idi:Reg1",   "/hdf_metadata_version")
    dark_begin           = Component(EpicsSignalDM, "8idi:Reg111", "/measurement/instrument/acquisition/dark_begin")
    dark_end             = Component(EpicsSignalDM, "8idi:Reg112", "/measurement/instrument/acquisition/dark_end")
    data_begin           = Component(EpicsSignalDM, "8idi:Reg113", "/measurement/instrument/acquisition/dark_end")
    data_end             = Component(EpicsSignalDM, "8idi:Reg114", "/measurement/instrument/acquisition/data_end")

    specscan_dark_number = Component(EpicsSignalDM, "8idi:Reg117", "/measurement/instrument/acquisition/specscan_dark_number")  # dtype='uint64'
    specscan_data_number = Component(EpicsSignalDM, "8idi:Reg118", "/measurement/instrument/acquisition/specscan_data_number")  # dtype='uint64'
    attenuation          = Component(EpicsSignalDM, "8idi:Reg110", "/measurement/instrument/acquisition/attenuation")
    beam_size_H          = Component(EpicsSignalDM, "8idi:Slit2Hsize", "/measurement/instrument/acquisition/beam_size_H")
    beam_size_V          = Component(EpicsSignalDM, "8idi:Slit3Vsize", "/measurement/instrument/acquisition/beam_size_V")

    specfile             = Component(EpicsSignalDM, "8idi:StrReg1", "/measurement/instrument/acquisition/specfile",      string=True)
    root_folder          = Component(EpicsSignalDM, "8idi:StrReg2", "/measurement/instrument/acquisition/root_folder",   string=True)
    parent_folder        = Component(EpicsSignalDM, "8idi:StrReg3", "/measurement/instrument/acquisition/parent_folder", string=True)
    data_folder          = Component(EpicsSignalDM, "8idi:StrReg4", "/measurement/instrument/acquisition/data_folder",   string=True)
    datafilename         = Component(EpicsSignalDM, "8idi:StrReg5", "/measurement/instrument/acquisition/datafilename",  string=True)

    beam_center_x        = Component(EpicsSignalDM, "8idi:Reg11",  "/measurement/instrument/acquisition/beam_center_x")
    beam_center_y        = Component(EpicsSignalDM, "8idi:Reg12",  "/measurement/instrument/acquisition/beam_center_y")
    stage_zero_x         = Component(EpicsSignalDM, "8idi:Reg13",  "/measurement/instrument/acquisition/stage_zero_x")
    stage_zero_z         = Component(EpicsSignalDM, "8idi:Reg14",  "/measurement/instrument/acquisition/stage_zero_z")
    stage_x              = Component(EpicsSignalDM, "8idi:Reg119", "/measurement/instrument/acquisition/stage_x")
    stage_z              = Component(EpicsSignalDM, "8idi:Reg120", "/measurement/instrument/acquisition/stage_z")
    
    # TODO: compression is represented as an enum
    # h5address = "/measurement/instrument/acquisition/compression"
    # f[h5address] = {True: "ENABLED", False: "DISABLED"}[compression == 1]
    
    # TODO: geometry needs help: if geometry == 0 (transmission): all values are -1

    # TODO: see how far we can get with this
