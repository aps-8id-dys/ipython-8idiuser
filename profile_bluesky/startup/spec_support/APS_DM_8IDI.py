
"""
support for the APS Data Management tools

Starting in January 2018, we are trying to move towards SDM Group product as part of DM or Data
Management developed by Sinisa Veseli. This primarily has tools to move data to the storage server with
cataloging tools. Additionally, this has workflow processing tools which are all done in python along with
shell scripts. With Faisal's new xpcs analysis toolkit, we will be using Sun Grid Engine (SGE) for job
submission. So it is time to move away from the Active MQ pipeline with the actors, etc. 

Sinisa has set up workflows: one for data transfer using GridFTP and the other to do full analysis. He has
also developed SGE submission and monitoring which is very helpful. The downside as of now is that there
is no GUI that shows the job status which was a plus with the old pipeline. A GUI will be developed in the
near future.

These workflows are stored in ~8idiuser/DM_Workflows/ and in https://subversion.xray.aps.anl.gov/xpcs/DM_Workflows/
"""

import datetime
import h5py
import logging
import math
import os
import subprocess
import threading

from . import detector_parameters

logger = logging.getLogger(os.path.split(__file__)[-1])


def unix(command, raises=True):
    """
    run a UNIX command, returns (stdout, stderr)

    from apstools.utils.unix()

    PARAMETERS
    
    command: str
        UNIX command to be executed
    raises: bool
        If `True`, will raise exceptions as needed,
        default: `True`
    """
    if sys.platform not in ("linux", "linux2"):
        emsg = f"Cannot call unix() when OS={sys.platform}"
        raise RuntimeError(emsg)

    process = subprocess.Popen(
        command, 
        shell=True,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        )

    stdout, stderr = process.communicate()

    if len(stderr) > 0:
        emsg = f"unix({command}) returned error:\n{stderr}"
        logger.error(emsg)
        if raises:
            raise RuntimeError(emsg)

    return stdout, stderr


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread

    from apstools.utils.run_in_thread()
    
    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       
       #...
       progress_reporting()   # runs in separate thread
       #...

    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class DM_Workflow:
    """
    support for the APS Data Management tools
        
    PARAMETERS
    
    registers : ophyd.Device or spec_DM_support.DataManagementMetadata
        Instance of class, connected to metadata register PVs
    
    transfer : str, optional
        Data Management Workflow transfer key (DM_WORKFLOW_DATA_TRANSFER)
    
    analysis : str, optional
        Data Management Workflow analysis key (DM_WORKFLOW_DATA_ANALYSIS)
    
    qmap_path : str, optional
        qmap file directory (QMAP_FOLDER_PATH)
    
    xpcs_qmap_file : str, optional
        XPCS qmap file name (XPCS_QMAP_FILENAME)

    ======================  ===========================================
    method                  docstring
    ======================  ===========================================
    get_workflow_filename   decide absolute file name for the APS data management workflow
    start_workflow          commence the APS data management workflow
    set_xpcs_qmap_file      (re)define the name of HDF5 workflow file
    create_hdf5_file        Reads camera data from EPICS PVs and writes to an hdf5 file
    DataTransfer            initiate data transfer
    DataAnalysis            initiate data analysis
    ListJobs                list current jobs in the workflow
    ======================  ===========================================
    """

    def __init__(self, 
                 registers,
                 aps_cycle,
                 xpcs_qmap_file,
                 transfer="xpcs8-01-Lambda",
                 analysis="xpcs8-02-Lambda",
                 ):
        self.registers = registers
        self.detectors = detector_parameters.PythonDict()

        self.DM_WORKFLOW_DATA_TRANSFER = transfer
        self.DM_WORKFLOW_DATA_ANALYSIS = analysis
        # self.DM_WORKFLOW_DATA_TRANSFER = "xpcs8-01-nos8iddata"
        # self.DM_WORKFLOW_DATA_ANALYSIS = "xpcs8-02-nos8iddata"
        self.TRANSFER_COMMAND = ""
        self.ANALYSIS_COMMAND = ""
        
        self.QMAP_FOLDER_PATH = f"/home/8-id-i/partitionMapLibrary/{aps_cycle}"
        self.XPCS_QMAP_FILENAME = self.set_xpcs_qmap_file(xpcs_qmap_file)

        self.hdf_workflow_file = None

    def get_workflow_filename(self):
        """
        decide absolute file name for the APS data management workflow
        """
        registers = self.registers
        path = registers.root_folder.value
        if path.startswith("/data"):
            path = os.path.join("/", "home", "8-id-i", *path.split("/")[2:])
        fname = (
            f"{registers.data_folder.value}"
            f"_{registers.data_begin.value:04.0f}"
            f"-{registers.data_end.value:04.0f}"
        )
        fullname = os.path.join(path, f"{fname}.hdf")
        suffix = 0
        while os.path.exists(fullname):
            suffix += 1
            fullname = os.path.join(path, f"{fname}__{suffix:03d}.hdf")
        if suffix > 0:
            logger.info(f"using modified file name: {fullname}")
        return fullname

    def start_workflow(self, analysis=True):
        """
        commence the APS data management workflow
        
        PARAMETERS
        
        hdf_workflow_file : str
            name of the HDF5 workflow file to be written
        
        analysis : bool
            If True (default): use DataAnalysis workflow.
            If False: use DataTransfer workflow.
        """
        self.hdf_workflow_file = self.get_workflow_filename()
        logger.debug(f"creating hdf_workflow_file = {self.hdf_workflow_file}")
        self.create_hdf5_file(self.hdf_workflow_file)

        @run_in_thread
        def kickoff_DM_workflow():
            logger.info(f"DM workflow starting: analysis:{analysis}  file:{hdf_workflow_file}")
            if analysis:
                out, err = self.DataAnalysis(self.hdf_workflow_file)
            else:
                out, err = self.DataTransfer(self.hdf_workflow_file)
            logger.info("DM workflow done")
            logger.info(out)
            if len(err) > 0:
                logger.error(err)
        
        # FIXME: kickoff_DM_workflow()

    def set_xpcs_qmap_file(self, xpcs_qmap_file):
        """
        (re)define the name of HDF5 workflow file
        
        PARAMETERS
        
        xpcs_qmap_file : str
            name of the HDF5 workflow file to be written
        """
        ext = ".h5"
        if not xpcs_qmap_file.endswith(ext):
            xpcs_qmap_file = os.path.splitext(xpcs_qmap_file)[0] + ext
        self.XPCS_QMAP_FILENAME = xpcs_qmap_file

    def create_hdf5_file(self, filename, **kwargs):
        """
        write metadata from EPICS PVs to new HDF5 file
        
        PARAMETERS
        
        filename : str
            name of the HDF5 file to be written
        """
        registers = self.registers

        # Gets Python Dict stored in other file
        masterDict = self.detectors.getMasterDict()

        logger.info(f"creating HDF5 file {filename}")
        
        # any exception here will be handled by caller
        with h5py.File(filename, "w-") as f:
            # get a version number so we can make changes without breaking client code
            f.create_dataset("/hdf_metadata_version",
                data=[[registers.hdf_metadata_version.value]]) #same as batchinfo_ver for now
            ##version 15 (May 2019) is start of burst mode support (rigaku) 

            #######/measurement/instrument/acquisition
            #######some new acq fields to replace batchinfo
            f.create_dataset("/measurement/instrument/acquisition/dark_begin",
                data=[[registers.dark_begin.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/dark_end",
                data=[[registers.dark_end.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/data_begin",
                data=[[registers.data_begin.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/data_end",
                data=[[registers.data_end.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/specscan_dark_number",
                data=[[registers.specscan_dark_number.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/specscan_data_number",
                data=[[registers.specscan_data_number.value]],
                dtype='uint64'
                )

            f.create_dataset("/measurement/instrument/acquisition/attenuation",
                data=[[registers.attenuation.value]])
            
            f.create_dataset("/measurement/instrument/acquisition/beam_size_H",
                data=[[registers.beam_size_H.value]])
            
            f.create_dataset("/measurement/instrument/acquisition/beam_size_V",
                data=[[registers.beam_size_V.value]])

            f["/measurement/instrument/acquisition/specfile"] = registers.specfile.value

            # registers.root_folder: '/home/8-id-i/2019-2/jemian_201908/A024/'
            # registers.data_subfolder: 'A186_DOHE04_Yb010_att0_Uq0_00150'
            # root_folder: '/home/8-id-i/2019-2/jemian_201908/A024/A186_DOHE04_Yb010_att0_Uq0_00150/'
            root_folder = os.path.join(
                registers.root_folder.value,
                registers.data_subfolder.value
            ).rstrip("/") + "/"  # ensure one and only one trailing `/`
            f["/measurement/instrument/acquisition/root_folder"] = root_folder

            # In [1]: registers.user_data_folder.value
            # Out[1]: '/home/8-id-i/2019-2/jemian_201908/A024'
            # pick "jemian_201908" part
            parent_folder = registers.user_data_folder.value
            if parent_folder.find("/") > -1:
                parent_folder = parent_folder.split("/")[-2]
            f["/measurement/instrument/acquisition/parent_folder"] = parent_folder

            f["/measurement/instrument/acquisition/data_folder"] = registers.data_folder.value
            f["/measurement/instrument/acquisition/datafilename"] = registers.datafilename.value

            f.create_dataset("/measurement/instrument/acquisition/beam_center_x",
                data=[[registers.beam_center_x.value]])

            f.create_dataset("/measurement/instrument/acquisition/beam_center_y",
                data=[[registers.beam_center_y.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_zero_x",
                data=[[registers.stage_zero_x.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_zero_z",
                data=[[registers.stage_zero_z.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_x",
                data=[[registers.stage_x.value]])

            f.create_dataset("/measurement/instrument/acquisition/stage_z",
                data=[[registers.stage_z.value]])

            v = {True: "ENABLED", 
                 False: "DISABLED"}[registers.compression.value == 1]
            f["/measurement/instrument/acquisition/compression"] = v

            if registers.geometry_num.value == 1: ##reflection geometry
                f.create_dataset("/measurement/instrument/acquisition/xspec",
                    data=[[float(registers.xspec.value)]],
                    dtype='float64')

                f.create_dataset("/measurement/instrument/acquisition/zspec",
                    data=[[float(registers.zspec.value)]],
                    dtype='float64')

                f.create_dataset("/measurement/instrument/acquisition/ccdxspec",
                    data=[[float(registers.ccdxspec.value)]],
                    dtype='float64')

                f.create_dataset("/measurement/instrument/acquisition/ccdzspec",
                    data=[[float(registers.ccdzspec.value)]],
                    dtype='float64')

                f.create_dataset("/measurement/instrument/acquisition/angle",
                    data=[[float(registers.angle.value)]],
                    dtype='float64')

            elif registers.geometry_num.value == 0: ##transmission geometry
                f["/measurement/instrument/acquisition/xspec"] = [[float(-1)]]
                f["/measurement/instrument/acquisition/zspec"] = [[float(-1)]]
                f["/measurement/instrument/acquisition/ccdxspec"] = [[float(-1)]]
                f["/measurement/instrument/acquisition/ccdzspec"] = [[float(-1)]]
                f["/measurement/instrument/acquisition/angle"] = [[float(-1)]]

            #/measurement/instrument/source_begin
            f.create_dataset("/measurement/instrument/source_begin/beam_intensity_incident",
                data=[[registers.source_begin_beam_intensity_incident.value]])

            f.create_dataset("/measurement/instrument/source_begin/beam_intensity_transmitted",
                data=[[registers.source_begin_beam_intensity_transmitted.value]])

            f.create_dataset("/measurement/instrument/source_begin/current",
                data=[[registers.source_begin_current.value]])
        
            f.create_dataset("/measurement/instrument/source_begin/energy",
			     data=[[registers.source_begin_energy.value]])

            f["/measurement/instrument/source_begin/datetime"] = registers.source_begin_datetime.value

            #/measurement/instrument/source_end (added in January 2019)
            f.create_dataset("/measurement/instrument/source_end/current",
                data=[[registers.source_end_current.value]])

            f["/measurement/instrument/source_end/datetime"] = registers.source_end_datetime.value

            ########################################################################################
            #/measurement/instrument/sample
            f.create_dataset("/measurement/sample/thickness", data=[[1.0]])
            
            f.create_dataset("/measurement/sample/temperature_A",
                data=[[registers.temperature_A.value]])

            f.create_dataset("/measurement/sample/temperature_B",
                data=[[registers.temperature_B.value]])

            f.create_dataset("/measurement/sample/temperature_A_set",
                data=[[registers.temperature_A_set.value]])
            # data=[[registers.pid1.value]])

            f.create_dataset("/measurement/sample/temperature_B_set",
                data=[[registers.temperature_B_set.value ]])

            f.create_dataset(
                "/measurement/sample/translation",
                data=[
                    [
                        registers.translation_x.value,
                        registers.translation_y.value,
                        registers.translation_z.value,
                        ]
                    ]
                )
            
            ##new dataset added on Oct 15,2018 (2018-3) to additionally add table params
            f.create_dataset(
                "/measurement/sample/translation_table",
                data=[
                    [
                        registers.translation_table_x.value,
                        registers.translation_table_y.value,
                        registers.translation_table_z.value,
                         ]
                    ]
                )

            f.create_dataset(
                "/measurement/sample/orientation",
                data=[
                    [
                        registers.sample_pitch.value,
                        registers.sample_roll.value,
                        registers.sample_yaw.value
                        ]
                    ]
                )

            #######/measurement/instrument/detector#########################
            detector_specs = masterDict[registers.detNum.value]

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
                data=[[registers.exposure_time.value]])

            f.create_dataset("/measurement/instrument/detector/exposure_period",
                data=[[registers.exposure_period.value]])

            if registers.burst_mode_state.value == 1:
                f.create_dataset("/measurement/instrument/detector/burst/number_of_bursts",
                    data=[[registers.number_of_bursts.value]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/burst/first_usable_burst",
                    data=[[registers.first_usable_burst.value]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/burst/last_usable_burst",
                    data=[[registers.last_usable_burst.value]], dtype='uint32')
            else:
                f.create_dataset("/measurement/instrument/detector/burst/number_of_bursts",
                    data=[[0]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/burst/first_usable_burst",
                    data=[[0]], dtype='uint32')
            
                f.create_dataset("/measurement/instrument/detector/burst/last_usable_burst",
                    data=[[0]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/distance",
                data=[[registers.detector_distance.value]])


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
            f.create_dataset("/measurement/instrument/detector/lld", 
                             data=[[float(v)]], 
                             dtype='float64')

            if detector_specs["lld"] > 0:
                v = float(detector_specs["lld"])
            else:
                v = 0.0
            f.create_dataset("/measurement/instrument/detector/sigma", data=[[v]], dtype='float64')

            f.create_dataset("/measurement/instrument/detector/gain", data=[[1]], dtype='uint32')

            choices = {0: "TRANSMISSION", 1: "REFLECTION"}
            v = choices.get(registers.geometry_num.value, "UNKNOWN")
            f["/measurement/instrument/detector/geometry"] = v

            choices = {True: "ENABLED", False: "DISABLED"}
            v = choices[registers.kinetics_state.value == 1]
            f["/measurement/instrument/detector/kinetics_enabled"] = v

            v = choices[registers.burst_mode_state.value == 1]
            f["/measurement/instrument/detector/burst_enabled"] = v

            #######/measurement/instrument/detector/kinetics/######
            if registers.kinetics_state.value == 1:
                f.create_dataset("/measurement/instrument/detector/kinetics/first_usable_window", 
                    data=[[2]], dtype='uint32')

                v = int(registers.kinetics_top.value/registers.kinetics_window_size.value)-1
                f.create_dataset("/measurement/instrument/detector/kinetics/last_usable_window", 
                    data=[[v]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/top", 
                    data=[[registers.kinetics_top.value]], dtype='uint32')

                f.create_dataset("/measurement/instrument/detector/kinetics/window_size", 
                    data=[[registers.kinetics_window_size.value]], dtype='uint32')
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
                data=[[registers.roi_x1.value]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/roi/y1", 
                data=[[registers.roi_y1.value]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/roi/x2", 
                data=[[registers.roi_x2.value]], dtype='uint32')

            f.create_dataset("/measurement/instrument/detector/roi/y2", 
                data=[[registers.roi_y2.value]], dtype='uint32')

        #####################################################################################
        # Close file closes automatically due to the "with" opener

    def DataTransfer(self, hdf_with_fullpath):
        """
        initiate data transfer
        """
        cmd = (
            "source /home/dm/etc/dm.setup.sh; "
            "dm-start-processing-job"
            f" --workflow-name={self.DM_WORKFLOW_DATA_TRANSFER}"
            f" filePath:{hdf_with_fullpath}"
            )
        self.TRANSFER_COMMAND = cmd;
        logger.info(
            "DM Workflow call is made for DATA transfer: "
            f"{hdf_with_fullpath}"
            f"----{datetime.datetime.now()}"
            )
        return unix(cmd)

    def DataAnalysis(self, 
                     hdf_with_fullpath, 
                     qmapfile_with_fullpath=None, 
                     xpcs_group_name=None):
        """
        initiate data analysis
        
        SPEC note: hdf_with_fullpath : usually saved in global HDF5_METADATA_FILE 
        """
        
        default = os.path.join(self.QMAP_FOLDER_PATH, self.XPCS_QMAP_FILENAME)
        qmapfile_with_fullpath = qmapfile_with_fullpath or default
        xpcs_group_name = xpcs_group_name or "/xpcs"

        cmd = (
            "source /home/dm/etc/dm.setup.sh; "
            "dm-start-processing-job"
            f" --workflow-name={self.DM_WORKFLOW_DATA_ANALYSIS}"
            f" filePath:{hdf_with_fullpath}"
            f" qmapFile:{qmapfile_with_fullpath}"
            f" xpcsGroupName:{xpcs_group_name}"
            )
        self.ANALYSIS_COMMAND = cmd;

        logger.info(
            f"DM Workflow call is made for XPCS Analysis: {hdf_with_fullpath}"
            f",{qmapfile_with_fullpath}"
            f"----{datetime.datetime.now()}"
            )
        return unix(cmd)

    def ListJobs(self):
        """
        list current jobs in the workflow
        """
        command = (
            "source /home/dm/etc/dm.setup.sh; "
            "dm-list-processing-jobs"
            " --display-keys=startTime,endTime,sgeJobName,status,stage,runTime,id"
            " | sort -r"
            " |head -n 10"
            )
        out, err = unix(command);
        logger.info("*"*30)
        logger.info(out)
        logger.info("*"*30)
