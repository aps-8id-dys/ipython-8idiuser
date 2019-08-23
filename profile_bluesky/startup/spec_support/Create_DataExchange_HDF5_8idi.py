
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

    def create_hdf5_file(self, filename):
        """
        write metadata to new HDF5 file
        """
        
        # Gets Python Dict stored in other file
        masterDict = self.obj.returnMasterDict()
        
        # any exception here will be handled by caller
        with h5py.File(filename, "w-") as f:

            # Metadata
            dt = h5py.special_dtype(vlen=unicode)
            data = 0

            # Gets Detector Number from a PV (for static fields)
            detNum = epics.caget('8idi:Reg2')

            # Gets Geometry Number from a PV (for static fields)
            geometry_num = epics.caget('8idi:Reg3')

            # Gets kinetics state from a PV (for static fields)
            kinetics_state = epics.caget('8idi:Reg107')
            burst_mode_state = epics.caget('8idi:Reg124')

            # Gets compression mode state from a PV (for static fields)
            compression = epics.caget('8idi:Reg8')

            # get a version number so we can make changes without breaking client code
            temp = f.create_dataset("/hdf_metadata_version", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg1') #same as batchinfo_ver for now
            ##version 15 (May 2019) is start of burst mode support (rigaku) 

            #######/measurement/instrument/acquisition
            #######some new acq fields to replace batchinfo
            temp = f.create_dataset("/measurement/instrument/acquisition/dark_begin", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg111')

            temp = f.create_dataset("/measurement/instrument/acquisition/dark_end", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg112')

            temp = f.create_dataset("/measurement/instrument/acquisition/data_begin", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg113')

            temp = f.create_dataset("/measurement/instrument/acquisition/data_end", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg114')

            temp = f.create_dataset("/measurement/instrument/acquisition/specscan_dark_number", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg117')

            temp = f.create_dataset("/measurement/instrument/acquisition/specscan_data_number", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg118')
            
            temp = f.create_dataset("/measurement/instrument/acquisition/attenuation", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg110')

            temp = f.create_dataset("/measurement/instrument/acquisition/beam_size_H", (1,1))
            temp[(0,0)] = epics.caget('8idi:Slit2Hsize.VAL')

            temp = f.create_dataset("/measurement/instrument/acquisition/beam_size_V", (1,1))
            temp[(0,0)] = epics.caget('8idi:Slit3Vsize.VAL')

            f["/measurement/instrument/acquisition/specfile"] = epics.caget('8idi:StrReg1',as_string=True)
            f["/measurement/instrument/acquisition/root_folder"] = epics.caget('8idi:StrReg2',as_string=True)
            f["/measurement/instrument/acquisition/parent_folder"] = epics.caget('8idi:StrReg3',as_string=True)
            f["/measurement/instrument/acquisition/data_folder"] = epics.caget('8idi:StrReg4',as_string=True)
            f["/measurement/instrument/acquisition/datafilename"] = epics.caget('8idi:StrReg5',as_string=True)

            ##standard fields continue
            temp = f.create_dataset("/measurement/instrument/acquisition/beam_center_x", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg11')

            temp = f.create_dataset("/measurement/instrument/acquisition/beam_center_y", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg12')

            temp = f.create_dataset("/measurement/instrument/acquisition/stage_zero_x", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg13')

            temp = f.create_dataset("/measurement/instrument/acquisition/stage_zero_z", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg14')

            temp = f.create_dataset("/measurement/instrument/acquisition/stage_x", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg119')

            temp = f.create_dataset("/measurement/instrument/acquisition/stage_z", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg120')

            h5address = "/measurement/instrument/acquisition/compression"
            f[h5address] = {True: "ENABLED", False: "DISABLED"}[compression == 1]

            if geometry_num == 1: ##reflection geometry
                temp = f.create_dataset("/measurement/instrument/acquisition/xspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg15')

                temp = f.create_dataset("/measurement/instrument/acquisition/zspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg16')

                temp = f.create_dataset("/measurement/instrument/acquisition/ccdxspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg18')

                temp = f.create_dataset("/measurement/instrument/acquisition/ccdzspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg17')

                temp = f.create_dataset("/measurement/instrument/acquisition/angle", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg19')

            if geometry_num == 0: ##transmission geometry
                temp = f.create_dataset("/measurement/instrument/acquisition/xspec", (1,1))
                temp[(0,0)] = -1

                temp = f.create_dataset("/measurement/instrument/acquisition/zspec", (1,1))
                temp[(0,0)] = -1

                temp = f.create_dataset("/measurement/instrument/acquisition/ccdxspec", (1,1))
                temp[(0,0)] = -1

                temp = f.create_dataset("/measurement/instrument/acquisition/ccdzspec", (1,1))
                temp[(0,0)] = -1

                temp = f.create_dataset("/measurement/instrument/acquisition/angle", (1,1))
                temp[(0,0)] = -1

            #/measurement/instrument/source_begin
            temp = f.create_dataset("/measurement/instrument/source_begin/beam_intensity_incident", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg9')

            temp = f.create_dataset("/measurement/instrument/source_begin/beam_intensity_transmitted", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg10')

            temp = f.create_dataset("/measurement/instrument/source_begin/current", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg121')
        
            temp = f.create_dataset("/measurement/instrument/source_begin/energy", (1,1))
            temp[(0,0)] = epics.caget('8idimono:sm2.RBV')
            
            f["/measurement/instrument/source_begin/datetime"] = epics.caget('8idi:StrReg6',as_string=True)

            #/measurement/instrument/source_end (added in January 2019)
            temp = f.create_dataset("/measurement/instrument/source_end/current", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg122')
        
            f["/measurement/instrument/source_end/datetime"] = epics.caget('8idi:StrReg7',as_string=True)

            ###############################################################################################################
            #/measurement/instrument/sample
            temp = f.create_dataset("/measurement/sample/thickness", (1,1))
            temp[(0,0)] = 1.0
            
            temp = f.create_dataset("/measurement/sample/temperature_A", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:IN1')

            temp = f.create_dataset("/measurement/sample/temperature_B", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:IN1')

            temp = f.create_dataset("/measurement/sample/temperature_A_set", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:OUT1:SP')
            ##temp[(0,0)] = epics.caget('8idi:pid1.VAL')

            temp = f.create_dataset("/measurement/sample/temperature_B_set", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:OUT1:SP')

            temp = f.create_dataset("/measurement/sample/translation", (1,3)) ##x,y,z
            temp[(0,0)] = epics.caget('8idi:m54.RBV')
            temp[(0,1)] = epics.caget('8idi:m49.RBV')
            temp[(0,2)] = epics.caget('8idi:m50.RBV')
            
            ##new dataset added on Oct 15,2018 (2018-3) to additionally add table params
            temp = f.create_dataset("/measurement/sample/translation_table", (1,3)) ##x,y,z
            temp[(0,0)] = epics.caget('8idi:TI3:x.VAL')
            temp[(0,1)] = epics.caget('8idi:TI3:z.VAL')
            temp[(0,2)] = epics.caget('8idi:TI3:y.VAL')

            temp = f.create_dataset("/measurement/sample/orientation", (1,3)) ##pitch,roll.yaw
            temp[(0,0)] = epics.caget('8idi:m52.RBV')
            temp[(0,1)] = epics.caget('8idi:m53.RBV')
            temp[(0,2)] = epics.caget('8idi:m51.RBV')

            #######/measurement/instrument/detector#########################
            detector_specs = masterDict[detNum]

            h5address = "/measurement/instrument/detector/manufacturer"
            f[h5address] = detector_specs["manufacturer"]

            ##f["/measurement/instrument/detector/model"] = 'UNKNOWN'
    
            ##f["/measurement/instrument/detector/serial_number"] = 'UNKNOWN'

            temp = f.create_dataset("/measurement/instrument/detector/bit_depth", (1,1),dtype='uint32')
            temp[(0,0)] = math.ceil(math.log(detector_specs["saturation"],2))

            temp = f.create_dataset("/measurement/instrument/detector/x_pixel_size", (1,1))
            temp[(0,0)] = detector_specs["dpix"]

            temp = f.create_dataset("/measurement/instrument/detector/y_pixel_size", (1,1))
            temp[(0,0)] = detector_specs["dpix"]

            temp = f.create_dataset("/measurement/instrument/detector/x_dimension", (1,1),dtype='uint32') 
            temp[(0,0)] = int(detector_specs["ccdHardwareColSize"])

            temp = f.create_dataset("/measurement/instrument/detector/y_dimension", (1,1),dtype='uint32')
            temp[(0,0)] = detector_specs["ccdHardwareRowSize"]

            temp = f.create_dataset("/measurement/instrument/detector/x_binning", (1,1),dtype='uint32')
            temp[(0,0)] = 1

            temp = f.create_dataset("/measurement/instrument/detector/y_binning", (1,1),dtype='uint32')
            temp[(0,0)] = 1

            temp = f.create_dataset("/measurement/instrument/detector/exposure_time", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg115')

            temp = f.create_dataset("/measurement/instrument/detector/exposure_period", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg116')

            temp = f.create_dataset("/measurement/instrument/detector/burst/number_of_bursts", (1,1),dtype='uint32')
            if burst_mode_state == 1:
                temp[(0,0)] = epics.caget("8idi:Reg125")
            else :
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/burst/first_usable_burst", (1,1),dtype='uint32')
            if burst_mode_state == 1:
                temp[(0,0)] = epics.caget("8idi:Reg126")
            else :
                temp[(0,0)] = 0
            
            temp = f.create_dataset("/measurement/instrument/detector/burst/last_usable_burst", (1,1),dtype='uint32')
            if burst_mode_state == 1:
                temp[(0,0)] = epics.caget("8idi:Reg127")
            else :
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/distance", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg5')


            if detector_specs["flatfield"] == 1:
                f["/measurement/instrument/detector/flatfield_enabled"] = 'ENABLED'
            else :
                f["/measurement/instrument/detector/flatfield_enabled"] = 'DISABLED'

            if detector_specs["blemish"] == 1:
                f["/measurement/instrument/detector/blemish_enabled"] = 'ENABLED'
            else :
                f["/measurement/instrument/detector/blemish_enabled"] = 'DISABLED'

            temp = f.create_dataset("/measurement/instrument/detector/efficiency", (1,1))
            temp[(0,0)] = detector_specs["efficiency"]

            temp = f.create_dataset("/measurement/instrument/detector/adu_per_photon", (1,1))
            temp[(0,0)] = detector_specs["adupphot"]

            temp = f.create_dataset("/measurement/instrument/detector/lld", (1,1))
            if detector_specs["lld"] < 0:
                temp[(0,0)] = abs(detector_specs["lld"])
            else:
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/sigma", (1,1))
            if detector_specs["lld"] > 0:
                temp[(0,0)] = detector_specs["lld"]
            else:
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/gain", (1,1),dtype='uint32')
            temp[(0,0)] = 1

            if geometry_num == 0:
                f["/measurement/instrument/detector/geometry"] = 'TRANSMISSION'
            elif geometry_num == 1:
                f["/measurement/instrument/detector/geometry"] = 'REFLECTION'
            else :
                f["/measurement/instrument/detector/geometry"] = 'UNKNOWN'

            if kinetics_state == 1:
                f["/measurement/instrument/detector/kinetics_enabled"] = 'ENABLED'
            else :
                f["/measurement/instrument/detector/kinetics_enabled"] = 'DISABLED'

            if burst_mode_state == 1:
                f["/measurement/instrument/detector/burst_enabled"] = 'ENABLED'
            else :
                f["/measurement/instrument/detector/burst_enabled"] = 'DISABLED'

            #######/measurement/instrument/detector/kinetics/######
            temp = f.create_dataset("/measurement/instrument/detector/kinetics/first_usable_window", (1,1),dtype='uint32')
            if kinetics_state == 1:
                temp[(0,0)] = 2 
            else :
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/kinetics/last_usable_window", (1,1),dtype='uint32')
            if  kinetics_state == 1:
                temp1slicetop = epics.caget("8idi:Reg109")
                temp1size = epics.caget("8idi:Reg108")
                temp[(0,0)] = int(temp1slicetop/temp1size)-1
            else :
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/kinetics/top", (1,1),dtype='uint32')
            if kinetics_state == 1:
                temp[(0,0)] = epics.caget('8idi:Reg109')
            else :
                temp[(0,0)] = 0

            temp = f.create_dataset("/measurement/instrument/detector/kinetics/window_size", (1,1),dtype='uint32')
            if kinetics_state == 1:
                temp[(0,0)] = epics.caget('8idi:Reg108')
            else :
                temp[(0,0)] = 0

            #######/measurement/instrument/detector/roi/######
            temp = f.create_dataset("/measurement/instrument/detector/roi/x1", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg101')

            temp = f.create_dataset("/measurement/instrument/detector/roi/y1", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg103')

            temp = f.create_dataset("/measurement/instrument/detector/roi/x2", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg102')

            temp = f.create_dataset("/measurement/instrument/detector/roi/y2", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg104')

        ###############################################################################################
        # Close file closes automatically due to the "with" opener


if __name__ == "__main__":
    filename = sys.argv[1]  # caller must provide a filename

    newObject = EigerHDF5()
    newObject.create_hdf5_file(filename)
   
