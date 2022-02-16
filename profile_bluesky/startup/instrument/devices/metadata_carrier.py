"""
Define common structures for configuration information.
"""

__all__ = [
    'basic_user_information',
    'qnw_parameters',
]


from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt
from bluesky import plan_stubs as bps

import json
import pathlib


QNW_JSON_FILE = "qnw_sample_info.json"


class BasicUserInformation(Device):
    """
    Specify basic user information at beginning of the run,
    i.e. scan directories, data directory, q map
    """

    det_directory = Cpt(Signal, value=None)
    scan_directory = Cpt(Signal, value=None)

    def select_path(self, user_index):
        """
        bluesky plan: set user directories
        """
        yield from bps.mv(
            self.det_directory, f'/home/8idiuser/{aps.aps_cycle.get()}/{user_index}',
            self.scan_directory, f'/home/beams10/8IDIUSER/bluesky_data/{aps.aps_cycle.get()}'
        )


    def select_qmap(self, qmap_name: str):
        """
        bluesky plan: set qmap
        """
        yield from bps.mv(self.qmapname, f'/home/8-id-i/{aps.aps_cycle.get()}/{qmap_name}')


basic_user_information = BasicUserInformation(name="basic_user_information")


class QnwParameters(Device):

    # TODO: Place holder. Need to merge this with QNW definition

    sample_name = Cpt(Signal, value=None)
    id_char = Cpt(Signal, value=None)
    samx_center = Cpt(Signal, value=None)
    samx_scan_halfwidth = Cpt(Signal, value=None)
    samx_num_points = Cpt(Signal, value=None)
    samz_center = Cpt(Signal, value=None)
    samz_scan_halfwidth = Cpt(Signal, value=None)
    samz_num_points = Cpt(Signal, value=None)
    qnw_position = Cpt(Signal, value=None)
    qnw_name = Cpt(Signal, value=None)

    def select(self, sample_index):
        """
        bluesky plan: Load sample information from json file.

        Reloads the json file containing sample info **every time** it's called.

        example json::

            {
                "sample1": {
                    "sample_name": "Test1",
                    "samp_id_char": "A",
                    "samx_center": 0,
                    "samx_scan_halfwidth": 0.1,
                    "samx_num_points": 11,
                    "samz_center": 0,
                    "samz_scan_halfwidth": 0.1,
                    "samz_num_points": 11,
                    "qnw_position": 147.5, 
                    "qnw_env": "qnw_env1"          
                }
            }
        """
        if basic_user_information.scan_directory.get() is None:
            raise ValueError(
                "'basic_user_information.scan_directory' is 'None'."
                "  Call 'basic_user_information.select_path(user_index)' first."
            )

        # look in user's directory for the JSON file
        path = pathlib.Path(basic_user_information.scan_directory.get())
        json_file = path / QNW_JSON_FILE
        with open(json_file, "r") as fp:  # open & read the JSON
            json_dict = json.load(fp)

        config = json_dict[sample_index]  # pick the sample
        yield from bps.mv(
            self.sample_name, config["sample_name"],
            self.id_char, config["samp_id_char"],
            self.samx_center, config["samx_center"],
            self.samx_scan_halfwidth, config["samx_scan_halfwidth"],
            self.samx_num_points, config["samx_num_points"],
            self.samz_center, config["samz_center"],
            self.samz_scan_halfwidth, config["samz_scan_halfwidth"],
            self.samz_num_points, config["samz_num_points"],
            self.qnw_position, config["qnw_position"],
            self.qnw_name, config["qnw_env"],
        )


qnw_parameters = QnwParameters(name="QnwParameters")
