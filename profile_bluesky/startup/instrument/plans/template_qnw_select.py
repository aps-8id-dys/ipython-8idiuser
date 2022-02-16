


class SampleInformation: 
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
