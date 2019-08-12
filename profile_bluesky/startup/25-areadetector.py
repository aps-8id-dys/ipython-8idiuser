logger.info(__file__)

"""area detector: X-Spectrum Lambda 750K"""

LAMBDA_750K_IOC_PREFIX = "8LAMBDA1:"

DATABROKER_ROOT_PATH = "/"
# AD_HDF5_IOC_WRITE_PATH = "/tmp/ADlambda/%Y/%m/%d/"     # FIXME: where will data be saved?
AD_HDF5_IOC_WRITE_PATH = "/home/8-id-i/bluesky-AD-data/%Y/%m/%d/"
AD_HDF5_DB_READ_PATH = AD_HDF5_IOC_WRITE_PATH


class Lambda750kCam(CamBase):
    """support for X-Spectrum Lambda 750K detector"""
    _html_docs = []
    temperature = Component(EpicsSignalWithRBV, 'Temperature')
    # TODO: What else?  Anything we'll configure or log.
    # config_file_path
    # operating_mode (with RBV)


# Use one of these plugins when configuring the HDF support:
#    Plugin_HDF5_Bluesky_Names  : Bluesky picks HDF5 file names, compatible with databroker
#    Plugin_HDF5_EPICS_Names    : EPICS user picks HDF5 file names, not compatible with databroker

class Plugin_HDF5_Bluesky_Names(
    HDF5Plugin, 
    FileStoreHDF5IterativeWrite
    ):
    create_directory_depth = Component(
        EpicsSignalWithRBV, 
        suffix="CreateDirectory")


class EpicsHdf5IterativeWriter(
    APS_devices.AD_EpicsHdf5FileName, # <-- code that uses EPICS naming
    FileStoreIterativeWrite
    ): pass
class Plugin_HDF5_EPICS_Names(
    HDF5Plugin, 
    EpicsHdf5IterativeWriter  # <-- custom from above
    ):
    create_directory_depth = Component(
        EpicsSignalWithRBV, 
        suffix="CreateDirectory")


class Lambda750kAreaDetector(SingleTrigger, AreaDetector): 
    cam = ADComponent(Lambda750kCam, "cam1:")
    image = Component(ImagePlugin, suffix="image1:")
    hdf1 = Component(
        Plugin_HDF5_EPICS_Names,
        suffix='HDF1:', 
        root = DATABROKER_ROOT_PATH,
        write_path_template = AD_HDF5_IOC_WRITE_PATH,
        read_path_template = AD_HDF5_DB_READ_PATH,
    )


try:
    adlambda = Lambda750kAreaDetector(
        LAMBDA_750K_IOC_PREFIX, 
        name='adlambda',
        )
    adlambda.read_attrs.append("hdf1")

    # suggestions for setting defaults
    # adlambda.hdf1.file_path.put(AD_HDF5_IOC_WRITE_PATH)
    # adlambda.hdf1.file_name.put("bluesky")
    # adlambda.hdf1.file_number.put(101)
    # adlambda.hdf1.array_counter.put(adlambda.hdf1.file_number.value)
    
except TimeoutError:
    m = "Could not connect Lambda 750K detector"
    m += f" with prefix  {LAMBDA_750K_IOC_PREFIX}"
    logger.warning(m)
