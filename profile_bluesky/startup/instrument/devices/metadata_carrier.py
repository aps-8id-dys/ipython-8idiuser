


__all__ = [
    'Init_User',
    'Init_QNW',
]


from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt
from bluesky import plan_stubs as bps


class Init_User(Device): 
    """
    Specify basic user information at beginning of the run,
    i.e. scan directories, data directory, q map
    """

    det_directory = Cpt(Signal, value=None)
    scan_directory = Cpt(Signal, value=None)

    def select_path(self, user_index):
        """
        set user directories
        """
        yield from bps.mv(self.det_directory, f'/home/8idiuser/{aps.aps_cycle.get()}/{user_index}')
        yield from bps.mv(self.scan_directory, f'/home/beams10/8IDIUSER/bluesky_data/{aps.aps_cycle.get()}')


    def select_qmap(self, qmap_name: str):
        """
        set qmap
        """
        yield from bps.mv(self.qmapname, f'/home/8-id-i/{aps.aps_cycle.get()}/{qmap_name}')


class Init_QNW(Device):

    # TO-DO: Place holder. Need to merge this with QNW definition
    # Make sure 'select' function reloads the json file containing sample info every time it's called
 
    def __init__(self):
        self.sample_name = None
        self.id_char = None
        self.samx_center = None
        self.samx_scan_halfwidth = None
        self.samx_num_points = None
        self.samz_center = None
        self.samz_scan_halfwidth = None
        self.samz_num_points = None
        self.qnw_position = None
        self.qnw_name = None
        
    def select(self, sample_index):
        """Load sample information from json file"""
        # read the json file
        # find the sample_index
        config = json_dict[sample_index]
        self.sample_name = ["sample_name"]
        self.id_char = ["samp_id_char"]











    
