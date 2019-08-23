##This file is meant to be called from SPEC so that it will create an hdf file
##that can replace .batchinfo
##Reads data from camera and puts it into an hdf5 file

import h5py
import epics
import sys
import PythonDict
import math
import datetime
import time

class EigerHDF5:
        def __init__(self):
            self.index=0
            self.obj = PythonDict.PythonDict()

        def begin(self):
            self.create_hdf5_file()

        def create_hdf5_file(self):
            """ Creates a new file based on name supplied via commandline and populates some metadata. """
            filename = sys.argv[1]
            try:
                self.f = h5py.File(filename, "w-")
            except Exception as ex:
                print("Error: %s" % ex)
                sys.exit(1)

            # Gets Python Dict stored in other file
            masterDict = self.obj.returnMasterDict()
            manufacturerDict = self.obj.returnManufacturerDict()
            
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
            temp = self.f.create_dataset("/hdf_metadata_version", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg1') #same as batchinfo_ver for now
        ##version 15 (May 2019) is start of burst mode support (rigaku) 

#######/measurement/instrument/acquisition
#######some new acq fields to replace batchinfo
            temp = self.f.create_dataset("/measurement/instrument/acquisition/dark_begin", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg111')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/dark_end", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg112')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/data_begin", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg113')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/data_end", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg114')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/specscan_dark_number", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg117')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/specscan_data_number", (1,1),dtype='uint64')
            temp[(0,0)] = epics.caget('8idi:Reg118')
            
            temp = self.f.create_dataset("/measurement/instrument/acquisition/attenuation", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg110')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/beam_size_H", (1,1))
            temp[(0,0)] = epics.caget('8idi:Slit2Hsize.VAL')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/beam_size_V", (1,1))
            temp[(0,0)] = epics.caget('8idi:Slit3Vsize.VAL')

            self.f["/measurement/instrument/acquisition/specfile"] = epics.caget('8idi:StrReg1',as_string=True)
            self.f["/measurement/instrument/acquisition/root_folder"] = epics.caget('8idi:StrReg2',as_string=True)
            self.f["/measurement/instrument/acquisition/parent_folder"] = epics.caget('8idi:StrReg3',as_string=True)
            self.f["/measurement/instrument/acquisition/data_folder"] = epics.caget('8idi:StrReg4',as_string=True)
            self.f["/measurement/instrument/acquisition/datafilename"] = epics.caget('8idi:StrReg5',as_string=True)

##standard fields continue
            temp = self.f.create_dataset("/measurement/instrument/acquisition/beam_center_x", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg11')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/beam_center_y", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg12')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/stage_zero_x", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg13')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/stage_zero_z", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg14')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/stage_x", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg119')

            temp = self.f.create_dataset("/measurement/instrument/acquisition/stage_z", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg120')

            if compression == 1:
                self.f["/measurement/instrument/acquisition/compression"] = 'ENABLED'
            else :
                self.f["/measurement/instrument/acquisition/compression"] = 'DISABLED'

            if geometry_num == 1: ##reflection geometry
                temp = self.f.create_dataset("/measurement/instrument/acquisition/xspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg15')

                temp = self.f.create_dataset("/measurement/instrument/acquisition/zspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg16')

                temp = self.f.create_dataset("/measurement/instrument/acquisition/ccdxspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg18')

                temp = self.f.create_dataset("/measurement/instrument/acquisition/ccdzspec", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg17')

                temp = self.f.create_dataset("/measurement/instrument/acquisition/angle", (1,1))
                temp[(0,0)] = epics.caget('8idi:Reg19')

            if geometry_num == 0: ##transmission geometry
                temp = self.f.create_dataset("/measurement/instrument/acquisition/xspec", (1,1))
                temp[(0,0)] = -1

                temp = self.f.create_dataset("/measurement/instrument/acquisition/zspec", (1,1))
                temp[(0,0)] = -1

                temp = self.f.create_dataset("/measurement/instrument/acquisition/ccdxspec", (1,1))
                temp[(0,0)] = -1

                temp = self.f.create_dataset("/measurement/instrument/acquisition/ccdzspec", (1,1))
                temp[(0,0)] = -1

                temp = self.f.create_dataset("/measurement/instrument/acquisition/angle", (1,1))
                temp[(0,0)] = -1

#/measurement/instrument/source_begin
            temp = self.f.create_dataset("/measurement/instrument/source_begin/beam_intensity_incident", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg9')

            temp = self.f.create_dataset("/measurement/instrument/source_begin/beam_intensity_transmitted", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg10')

            temp = self.f.create_dataset("/measurement/instrument/source_begin/current", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg121')
        
            temp = self.f.create_dataset("/measurement/instrument/source_begin/energy", (1,1))
            temp[(0,0)] = epics.caget('8idimono:sm2.RBV')
            
            self.f["/measurement/instrument/source_begin/datetime"] = epics.caget('8idi:StrReg6',as_string=True)

#/measurement/instrument/source_end (added in January 2019)
            temp = self.f.create_dataset("/measurement/instrument/source_end/current", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg122')
        
            self.f["/measurement/instrument/source_end/datetime"] = epics.caget('8idi:StrReg7',as_string=True)

###############################################################################################################
#/measurement/instrument/sample
            temp = self.f.create_dataset("/measurement/sample/thickness", (1,1))
            temp[(0,0)] = 1.0
            
            temp = self.f.create_dataset("/measurement/sample/temperature_A", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:IN1')

            temp = self.f.create_dataset("/measurement/sample/temperature_B", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:IN1')

            temp = self.f.create_dataset("/measurement/sample/temperature_A_set", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:OUT1:SP')
            ##temp[(0,0)] = epics.caget('8idi:pid1.VAL')

            temp = self.f.create_dataset("/measurement/sample/temperature_B_set", (1,1))
            temp[(0,0)] = epics.caget('8idi:LS336:TC4:OUT1:SP')

            temp = self.f.create_dataset("/measurement/sample/translation", (1,3)) ##x,y,z
            temp[(0,0)] = epics.caget('8idi:m54.RBV')
            temp[(0,1)] = epics.caget('8idi:m49.RBV')
            temp[(0,2)] = epics.caget('8idi:m50.RBV')
            
            ##new dataset added on Oct 15,2018 (2018-3) to additionally add table params
            temp = self.f.create_dataset("/measurement/sample/translation_table", (1,3)) ##x,y,z
            temp[(0,0)] = epics.caget('8idi:TI3:x.VAL')
            temp[(0,1)] = epics.caget('8idi:TI3:z.VAL')
            temp[(0,2)] = epics.caget('8idi:TI3:y.VAL')

            temp = self.f.create_dataset("/measurement/sample/orientation", (1,3)) ##pitch,roll.yaw
            temp[(0,0)] = epics.caget('8idi:m52.RBV')
            temp[(0,1)] = epics.caget('8idi:m53.RBV')
            temp[(0,2)] = epics.caget('8idi:m51.RBV')

#######/measurement/instrument/detector#########################
            try:
                self.f["/measurement/instrument/detector/manufacturer"] = manufacturerDict[detNum]
            except KeyError:
                self.f["/measurement/instrument/detector/manufacturer"] = 'UNKNOWN'

        ##self.f["/measurement/instrument/detector/model"] = 'UNKNOWN'

        ##self.f["/measurement/instrument/detector/serial_number"] = 'UNKNOWN'

            temp = self.f.create_dataset("/measurement/instrument/detector/bit_depth", (1,1),dtype='uint32')
            temp[(0,0)] = math.ceil(math.log(masterDict[detNum]["saturation"],2))

            temp = self.f.create_dataset("/measurement/instrument/detector/x_pixel_size", (1,1))
            temp[(0,0)] = masterDict[detNum]["dpix"]

            temp = self.f.create_dataset("/measurement/instrument/detector/y_pixel_size", (1,1))
            temp[(0,0)] = masterDict[detNum]["dpix"]

            temp = self.f.create_dataset("/measurement/instrument/detector/x_dimension", (1,1),dtype='uint32') 
            temp[(0,0)] = int(masterDict[detNum]["ccdHardwareColSize"])

            temp = self.f.create_dataset("/measurement/instrument/detector/y_dimension", (1,1),dtype='uint32')
            temp[(0,0)] = masterDict[detNum]["ccdHardwareRowSize"]

            temp = self.f.create_dataset("/measurement/instrument/detector/x_binning", (1,1),dtype='uint32')
            temp[(0,0)] = 1

            temp = self.f.create_dataset("/measurement/instrument/detector/y_binning", (1,1),dtype='uint32')
            temp[(0,0)] = 1

            temp = self.f.create_dataset("/measurement/instrument/detector/exposure_time", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg115')

            temp = self.f.create_dataset("/measurement/instrument/detector/exposure_period", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg116')

            temp = self.f.create_dataset("/measurement/instrument/detector/burst/number_of_bursts", (1,1),dtype='uint32')
            if burst_mode_state == 1:
                temp[(0,0)] = epics.caget("8idi:Reg125")
            else :
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/burst/first_usable_burst", (1,1),dtype='uint32')
            if burst_mode_state == 1:
                temp[(0,0)] = epics.caget("8idi:Reg126")
            else :
                temp[(0,0)] = 0
            
            temp = self.f.create_dataset("/measurement/instrument/detector/burst/last_usable_burst", (1,1),dtype='uint32')
            if burst_mode_state == 1:
                temp[(0,0)] = epics.caget("8idi:Reg127")
            else :
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/distance", (1,1))
            temp[(0,0)] = epics.caget('8idi:Reg5')


            if masterDict[detNum]["flatfield"] == 1:
                self.f["/measurement/instrument/detector/flatfield_enabled"] = 'ENABLED'
            else :
                self.f["/measurement/instrument/detector/flatfield_enabled"] = 'DISABLED'

            if masterDict[detNum]["blemish"] == 1:
                self.f["/measurement/instrument/detector/blemish_enabled"] = 'ENABLED'
            else :
                self.f["/measurement/instrument/detector/blemish_enabled"] = 'DISABLED'

            temp = self.f.create_dataset("/measurement/instrument/detector/efficiency", (1,1))
            temp[(0,0)] = masterDict[detNum]["efficiency"]

            temp = self.f.create_dataset("/measurement/instrument/detector/adu_per_photon", (1,1))
            temp[(0,0)] = masterDict[detNum]["adupphot"]

            temp = self.f.create_dataset("/measurement/instrument/detector/lld", (1,1))
            if masterDict[detNum]["lld"] < 0:
                temp[(0,0)] = abs(masterDict[detNum]["lld"])
            else:
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/sigma", (1,1))
            if masterDict[detNum]["lld"] > 0:
                temp[(0,0)] = masterDict[detNum]["lld"]
            else:
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/gain", (1,1),dtype='uint32')
            temp[(0,0)] = 1

            if geometry_num == 0:
                self.f["/measurement/instrument/detector/geometry"] = 'TRANSMISSION'
            elif geometry_num == 1:
                self.f["/measurement/instrument/detector/geometry"] = 'REFLECTION'
            else :
                self.f["/measurement/instrument/detector/geometry"] = 'UNKNOWN'

            if kinetics_state == 1:
                self.f["/measurement/instrument/detector/kinetics_enabled"] = 'ENABLED'
            else :
                self.f["/measurement/instrument/detector/kinetics_enabled"] = 'DISABLED'

            if burst_mode_state == 1:
                self.f["/measurement/instrument/detector/burst_enabled"] = 'ENABLED'
            else :
                self.f["/measurement/instrument/detector/burst_enabled"] = 'DISABLED'
#######/measurement/instrument/detector/kinetics/######
            temp = self.f.create_dataset("/measurement/instrument/detector/kinetics/first_usable_window", (1,1),dtype='uint32')
            if kinetics_state == 1:
                temp[(0,0)] = 2 
            else :
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/kinetics/last_usable_window", (1,1),dtype='uint32')
            if  kinetics_state == 1:
                temp1slicetop = epics.caget("8idi:Reg109")
                temp1size = epics.caget("8idi:Reg108")
                temp[(0,0)] = int(temp1slicetop/temp1size)-1
            else :
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/kinetics/top", (1,1),dtype='uint32')
            if kinetics_state == 1:
                temp[(0,0)] = epics.caget('8idi:Reg109')
            else :
                temp[(0,0)] = 0

            temp = self.f.create_dataset("/measurement/instrument/detector/kinetics/window_size", (1,1),dtype='uint32')
            if kinetics_state == 1:
                temp[(0,0)] = epics.caget('8idi:Reg108')
            else :
                temp[(0,0)] = 0

#######/measurement/instrument/detector/roi/######
            temp = self.f.create_dataset("/measurement/instrument/detector/roi/x1", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg101')

            temp = self.f.create_dataset("/measurement/instrument/detector/roi/y1", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg103')

            temp = self.f.create_dataset("/measurement/instrument/detector/roi/x2", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg102')

            temp = self.f.create_dataset("/measurement/instrument/detector/roi/y2", (1,1),dtype='uint32')
            temp[(0,0)] = epics.caget('8idi:Reg104')

###############################################################################################
            # Close file
            self.f.close()  

newObject=EigerHDF5()
newObject.begin()
###############################################################################################
