
"""
Reads camera data from EPICS PVs and writes to an hdf5 file

This file is meant to be called from SPEC
that can replace .batchinfo
"""

import datetime
import epics
import h5py
import math
import sys
import time

from . import detector_parameters


class EigerHDF5:
    def __init__(self):
        self.index = 0      # TODO: How is this used?
        self.obj = detector_parameters.PythonDict()

    # def begin(self, filename):
    #     # TODO: Why is this method needed?
    #     # Why not call create_hdf5_file() directly?
    #     self.create_hdf5_file(filename)

    def create_hdf5_file(self, filename, as_bluesky_plan=False):
        """
        write metadata from EPICS PVs to new HDF5 file
        """
        
        if as_bluesky_plan:
            # make this a bluesky plan, MUST yield at least one Message
            # This is the only statement here that makes this a bluesky plan
            yield from bps.null()

        # Gets Python Dict stored in other file
        masterDict = self.obj.returnMasterDict()
        
        # any exception here will be handled by caller
        with h5py.File(filename, "w-") as f:

            # Metadata
            dt = h5py.special_dtype(vlen=unicode)   # TODO: not used below, what does it do?
            data = 0

            # get a version number so we can make changes without breaking client code
            f.create_dataset("/hdf_metadata_version",
                data=[[dm_pars.hdf_metadata_version.value]]) #same as batchinfo_ver for now
            ##version 15 (May 2019) is start of burst mode support (rigaku) 

            #######/measurement/instrument/acquisition
            #######some new acq fields to replace batchinfo
            f.create_dataset("/measurement/instrument/acquisition/dark_begin",
                data=[[dm_pars.dark_begin.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/dark_end",
                data=[[dm_pars.dark_end.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/data_begin",
                data=[[dm_pars.data_begin.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/data_end",
                data=[[dm_pars.data_end.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/specscan_dark_number",
                data=[[dm_pars.specscan_dark_number.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/specscan_data_number",
                data=[[dm_pars.specscan_data_number.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/attenuation",
                data=[[dm_pars.attenuation.value]])
            
            f.create_dataset("/measurement/instrument/acquisition/beam_size_H",
                data=[[dm_pars.beam_size_H.value]])
            
            f.create_dataset("/measurement/instrument/acquisition/beam_size_V",
                data=[[dm_pars.beam_size_V.value]])

            f["/measurement/instrument/acquisition/specfile"] = dm_pars.specfile.value
            f["/measurement/instrument/acquisition/root_folder"] = dm_pars.root_folder.value
            f["/measurement/instrument/acquisition/parent_folder"] = dm_pars.parent_folder.value
            f["/measurement/instrument/acquisition/data_folder"] = dm_pars.data_folder.value
            f["/measurement/instrument/acquisition/datafilename"] = dm_pars.datafilename.value

            f.create_dataset("/measurement/instrument/acquisition/beam_center_x",
                data=[[dm_pars.beam_center_x.value]])

            f.create_dataset("/measurement/instrument/acquisition/beam_center_y",
                data=[[dm_pars.beam_center_y.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_zero_x",
                data=[[dm_pars.stage_zero_x.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_zero_z",
                data=[[dm_pars.stage_zero_z.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_x",
                data=[[dm_pars.stage_x.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_z",
                data=[[dm_pars.stage_z.value]])

            v = {True: "ENABLED", 
                 False: "DISABLED"}[dm_pars.compression.value == 1]
            f["/measurement/instrument/acquisition/compression"] = v

            if dm_pars.geometry_num.value == 1: ##reflection geometry
                f.create_dataset("/measurement/instrument/acquisition/xspec",
                    data=[[dm_pars.xspec.value]])

                f.create_dataset("/measurement/instrument/acquisition/zspec",
                    data=[[dm_pars.zspec.value]])

                f.create_dataset("/measurement/instrument/acquisition/ccdxspec",
                    data=[[dm_pars.ccdxspec.value]])

                f.create_dataset("/measurement/instrument/acquisition/ccdzspec",
                    data=[[dm_pars.ccdzspec.value]])

                f.create_dataset("/measurement/instrument/acquisition/angle",
                    data=[[dm_pars.angle.value]])

            if dm_pars.geometry_num.value == 0: ##transmission geometry
                f["/measurement/instrument/acquisition/xspec"] = [[-1]]
                f["/measurement/instrument/acquisition/zspec"] = [[-1]]
                f["/measurement/instrument/acquisition/ccdxspec"] = [[-1]]
                f["/measurement/instrument/acquisition/ccdzspec"] = [[-1]]
                f["/measurement/instrument/acquisition/angle"] = [[-1]]

            #/measurement/instrument/source_begin
            f.create_dataset("/measurement/instrument/source_begin/beam_intensity_incident",
                data=[[dm_pars.source_begin_beam_intensity_incident.value]])

            f.create_dataset("/measurement/instrument/source_begin/beam_intensity_transmitted",
                data=[[dm_pars.source_begin_beam_intensity_transmitted.value]])

            f.create_dataset("/measurement/instrument/source_begin/current",
                data=[[dm_pars.source_begin_current.value]])
        
            f.create_dataset("/measurement/instrument/source_begin/energy",
                data=[[dm_pars.source_begin_energy.value]])

            f["/measurement/instrument/source_begin/datetime"] = dm_pars.source_begin_datetime.value

            #/measurement/instrument/source_end (added in January 2019)
            f.create_dataset("/measurement/instrument/source_end/current",
                data=[[dm_pars.source_end_current.value]])

            f["/measurement/instrument/source_end/datetime"] = dm_pars.source_end_datetime.value

            ########################################################################################
            #/measurement/instrument/sample
            f.create_dataset("/measurement/sample/thickness", data=[[1.0]])
            
            f.create_dataset("/measurement/sample/temperature_A",
                data=[[dm_pars.temperature_A.value]])

            f.create_dataset("/measurement/sample/temperature_B",
                data=[[dm_pars.temperature_B.value]])

            f.create_dataset("/measurement/sample/temperature_A_set",
                data=[[dm_pars.temperature_A_set.value]])
            # data=[[dm_pars.pid1.value]])

            f.create_dataset("/measurement/sample/temperature_B_set",
                data=[[dm_pars.temperature_B_set.value]])

            f.create_dataset(
                "/measurement/sample/translation",
                data=[
                    [
                        dm_pars.translation_x.value,
                        dm_pars.translation_y.value,
                        dm_pars.translation_z.value,
                        ]
                    ]
                )
            
            ##new dataset added on Oct 15,2018 (2018-3) to additionally add table params
            f.create_dataset(
                "/measurement/sample/translation_table",
                data=[
                    [
                        dm_pars.translation_table_x.value,
                        dm_pars.translation_table_y.value,
                        dm_pars.translation_table_z.value,
                        ]
                    ]
                )

            f.create_dataset(
                "/measurement/sample/orientation",
                data=[
                    [
                        dm_pars.sample_roll.value,
                        dm_pars.sample_pitch.value,
                        dm_pars.sample_yaw.value,
                        ]
                    ]
                )

            #######/measurement/instrument/detector#########################
            detector_specs = masterDict[dm_pars.detNum.value]

            f["/measurement/instrument/detector/manufacturer"] = detector_specs["manufacturer"]

            ##f["/measurement/instrument/detector/model"] = detector_specs.get("model", "UNKNOWN")
    
            ##f["/measurement/instrument/detector/serial_number"] = detector_specs.get("serial_number", "UNKNOWN")

            f.create_dataset("/measurement/instrument/detector/bit_depth",
                data=[[math.ceil(math.log(detector_specs["saturation"],2))]],
                dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/x_pixel_size",
                data=[[detector_specs["dpix"]]])

            f.create_dataset("/measurement/instrument/detector/y_pixel_size",
                data=[[detector_specs["dpix"]]])

            f.create_dataset("/measurement/instrument/detector/x_dimension",
                data=[[int(detector_specs["ccdHardwareColSize"])]],
                dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/y_dimension",
                data=[[int(detector_specs["ccdHardwareRowSize"])]],
                dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/x_binning",
                data=[[1]],
                dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/y_binning",
                data=[[1]],
                dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/exposure_time",
                data=[[dm_pars.exposure_time.value]])

            f.create_dataset("/measurement/instrument/detector/exposure_period",
                data=[[dm_pars.exposure_period.value]])

            if dm_pars.burst_mode_state.value == 1:
                f.create_dataset("/measurement/instrument/detector/burst/number_of_bursts",
                    data=[[dm_pars.number_of_bursts.value]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/burst/first_usable_burst",
                    data=[[dm_pars.first_usable_burst.value]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/burst/last_usable_burst",
                    data=[[dm_pars.last_usable_burst.value]], dtype='uint32')
            else:
                f.create_dataset("/measurement/instrument/detector/burst/number_of_bursts",
                    data=[[0]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/burst/first_usable_burst",
                    data=[[0]], dtype='uint32')
            
                f.create_dataset("/measurement/instrument/detector/burst/last_usable_burst",
                    data=[[0]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/distance",
                data=[[dm_pars.detector_distance.value]])


            choices = {True: "ENABLED", False: "DISABLED"}
            v = choices[detector_specs["flatfield"] == 1]
            f["/measurement/instrument/detector/flatfield_enabled"] = v

            # same choices
            v = choices[detector_specs["blemish"] == 1]
            f["/measurement/instrument/detector/blemish_enabled"] = v

            f.create_dataset("/measurement/instrument/detector/efficiency",
                data=[[detector_specs["efficiency"]]])

            f.create_dataset("/measurement/instrument/detector/adu_per_photon",
                data=[[detector_specs["adupphot"]]])

            if detector_specs["lld"] < 0:
                v = abs(detector_specs["lld"])
            else:
                v = 0
            f.create_dataset("/measurement/instrument/detector/lld", data=[[v]])

            if detector_specs["lld"] > 0:
                v = detector_specs["lld"]
            else:
                v = 0
            f.create_dataset("/measurement/instrument/detector/sigma", data=[[v]])

            f.create_dataset("/measurement/instrument/detector/gain", data=[[1]], dtype='uint32')

            choices = {0: "TRANSMISSION", 1: "REFLECTION"}
            v = choices.get(dm_pars.geometry_num.value, "UNKNOWN")
            f["/measurement/instrument/detector/flatfield_enabled"] = v

            choices = {True: "ENABLED", False: "DISABLED"}
            v = choices[dm_pars.kinetics_state.value == 1]
            f["/measurement/instrument/detector/kinetics_enabled"] = v

            v = choices[dm_pars.burst_mode_state.value == 1]
            f["/measurement/instrument/detector/burst_enabled"] = v

            #######/measurement/instrument/detector/kinetics/######
            if dm_pars.kinetics_state.value == 1:
                f.create_dataset("/measurement/instrument/detector/kinetics/first_usable_window", 
                    data=[[2]], dtype='uint32')

                v = int(dm_pars.kinetics_top.value/dm_pars.kinetics_window_size.value)-1
                f.create_dataset("/measurement/instrument/detector/kinetics/last_usable_window", 
                    data=[[v]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/top", 
                    data=[[dm_pars.kinetics_top.value]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/window_size", 
                    data=[[dm_pars.kinetics_window_size.value]], dtype='uint32')
            else :
                f.create_dataset("/measurement/instrument/detector/kinetics/first_usable_window", 
                    data=[[0]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/last_usable_window", 
                    data=[[0]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/top", 
                    data=[[0]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/window_size", 
                    data=[[0]], dtype='uint32')

            #######/measurement/instrument/detector/roi/######
            f.create_dataset("/measurement/instrument/detector/roi/x1", 
                data=[[dm_pars.roi_x1.value]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/roi/y1", 
                data=[[dm_pars.roi_y1.value]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/roi/x2", 
                data=[[dm_pars.roi_x2.value]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/roi/y2", 
                data=[[dm_pars.roi_y2.value]], dtype='uint32')

        #####################################################################################
        # Close file closes automatically due to the "with" opener


if __name__ == "__main__":
    filename = sys.argv[1]  # caller must provide a filename

    newObject = EigerHDF5()
    newObject.create_hdf5_file(filename)
   
