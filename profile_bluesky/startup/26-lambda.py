logger.info(__file__)

"""X-Spectrum Lambda 750K (not `ophyd.areaDetector`)"""

from ophyd.device import Staged

LAMBDA_750K_IOC_PREFIX = "8LAMBDA1:"


class Lambda750kCamLocal(Device):
    """
    local interface to the ADLambda 750k cam1 plugin
    """
    # implement just the parts needed from ophyd.areaDetector
    acquire = Component(EpicsSignal, "Acquire")
    acquire_period = Component(____FIXME____, "____FIXME____")
    acquire_time = Component(____FIXME____, "____FIXME____")
    num_images = Component(____FIXME____, "____FIXME____")
    blocking_callbacks = Component(____FIXME____, "____FIXME____")

    config_file_path = Component(EpicsSignal, 'ConfigFilePath')
    firmware_version = Component(EpicsSignalRO, 'FirmwareVersion_RBV')
    operating_mode = Component(EpicsSignalWithRBV, 'OperatingMode')
    serial_number = Component(EpicsSignalRO, 'SerialNumber_RBV')
    temperature = Component(EpicsSignalWithRBV, 'Temperature')


class IMMoutLocal(Device):
    """
    local interface to the IMMout plugin
    """
    # implement just the parts needed from ophyd.areaDetector
    blocking_callbacks = Component(____FIXME____, "____FIXME____")
    capture = Component(EpicsSignalWithRBV, "Capture")
    enable = Component(____FIXME____, "____FIXME____")
    file_format = Component(EpicsSignalWithRBV, 'NDFileIMM_format')
    file_name = Component(____FIXME____, "____FIXME____")
    file_number = Component(____FIXME____, "____FIXME____")
    file_path = Component(____FIXME____, "____FIXME____")
    full_file_name = Component(EpicsSignalWithRBV, "____FIXME____")
    num_capture = Component(____FIXME____, "____FIXME____")
    num_captured = Component(EpicsSignalWithRBV, "____FIXME____")

    unique_id = Component(EpicsSignalRO, 'NDFileIMM_uniqueID_RBV')


class Lambda750kLocal(Device):
    """
    local interface to the Lambda 750k detector
    """
    # implement just the parts needed from ophyd.areaDetector
    detector_number = 25    # 8-ID-I numbering of this detector

    # only need cam1 and IMMout plugins
    cam = Component(Lambda750kCamLocal, "cam1:")
    immout = Component(IMMoutLocal, "IMMout:")

    def trigger(self):
        # FIXME:
        ...
    
    @property
    def plugin_file_name(self):
        """
        return the file name the plugin wrote
        
        Implement for the DM workflow.
        """
        # cut the path from file name
        return os.path.basename(self.immout.full_file_name.value)
    
    @property
    def images_received(self):
        return self.immout.num_captured.get()
    
    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the detector's stage_sigs for acquisition with the DM workflow
        
        Implement this method in _any_ Device that requires custom
        setup for the DM workflow.
        """
        if len(args) != 5:
            raise IndexError(f"expected 5 parameters, received {len(args)}: args={args}")
        file_path = args[0]
        file_name = args[1]
        num_images = args[2]
        acquire_time = args[3]
        acquire_period = args[4]

        self.cam.stage_sigs["num_images"] = num_images
        self.cam.stage_sigs["acquire_time"] = acquire_time
        self.cam.stage_sigs["acquire_period"] = acquire_period
        self.immout.stage_sigs["enable"] = 1
        self.immout.stage_sigs["blocking_callbacks"] = "Yes"
        self.immout.stage_sigs["parent.cam.array_callbacks"] = 1
        self.immout.stage_sigs["file_path"] = file_path
        self.immout.stage_sigs["file_name"] = file_name
        self.immout.stage_sigs["num_capture"] = num_images
        self.immout.stage_sigs["file_number"] = 1
        self.immout.stage_sigs["file_format"] = "IMM_Cmprs"
        self.immout.stage_sigs["capture"] = 1

try:
    lambdadet = Lambda750kLocal(
        LAMBDA_750K_IOC_PREFIX, 
        name='lambdadet',
        labels=["lambda",]
        )

    lambdadet.read_attrs += ["immout", ]
    
except TimeoutError:
    m = "Could not connect Lambda 750K detector"
    m += f" with prefix  {LAMBDA_750K_IOC_PREFIX}"
    logger.warning(m)
