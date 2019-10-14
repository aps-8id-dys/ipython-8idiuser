logger.info(__file__)

"""X-Spectrum Lambda 750K (not `ophyd.areaDetector`)"""

from ophyd.device import Staged

LAMBDA_750K_IOC_PREFIX = "8LAMBDA1:"


class Lambda750kCamLocal(Device):
    """
    local interface to the ADLambda 750k cam1 plugin
    """
    # implement just the parts needed by our data acquisition
    acquire = Component(EpicsSignalWithRBV, "Acquire", trigger_value=1, kind='config')
    acquire_period = Component(EpicsSignalWithRBV, "AcquirePeriod", kind='config')
    acquire_time = Component(EpicsSignalWithRBV, "AcquireTime", kind='config')
    array_callbacks = Component(EpicsSignalWithRBV, "ArrayCallbacks", kind='config')
    num_images = Component(EpicsSignalWithRBV, "NumImages")
    # blocking_callbacks = Component(EpicsSignalWithRBV, "BlockingCallbacks")

    config_file_path = Component(EpicsSignal, 'ConfigFilePath', string=True, kind='config')
    firmware_version = Component(EpicsSignalRO, 'FirmwareVersion_RBV', string=True, kind='config')
    operating_mode = Component(EpicsSignalWithRBV, 'OperatingMode', kind='config')
    serial_number = Component(EpicsSignalRO, 'SerialNumber_RBV', string=True, kind='config')
    temperature = Component(EpicsSignalWithRBV, 'Temperature', kind='config')


class IMMoutLocal(Device):
    """
    local interface to the IMMout plugin
    """
    # implement just the parts needed by our data acquisition
    blocking_callbacks = Component(EpicsSignalWithRBV, "BlockingCallbacks", kind='config')
    capture = Component(EpicsSignalWithRBV, "Capture", kind='config')
    enable = Component(EpicsSignalWithRBV, "EnableCallbacks", string=True, kind="config")
    file_format = Component(EpicsSignalWithRBV, "NDFileIMM_format", string=True, kind="config")
    file_name = Component(EpicsSignalWithRBV, "FileName", string=True, kind='config')
    file_number = Component(EpicsSignalWithRBV, "FileNumber", kind='config')
    file_path = Component(EpicsSignalWithRBV, "FilePath", string=True, kind='config')
    full_file_name = Component(EpicsSignalRO, "FullFileName_RBV", string=True, kind='config')
    num_capture = Component(EpicsSignalWithRBV, "NumCapture", kind='config')
    num_captured = Component(EpicsSignalRO, "NumCaptured_RBV")

    unique_id = Component(EpicsSignalRO, 'NDFileIMM_uniqueID_RBV')


class Lambda750kLocal(Device):
    """
    local interface to the Lambda 750k detector
    """
    # implement just the parts needed by our data acquisition
    detector_number = 25    # 8-ID-I numbering of this detector

    # only need cam1 and IMMout plugins
    cam = Component(Lambda750kCamLocal, "cam1:")
    immout = Component(IMMoutLocal, "IMMout:")

    def trigger(self):
        "trigger device acquisition and return a status object"
        acquire_signal = self.cam.acquire
        start_value = 1
        done_value = 0
        # watch_signal = self.cam.acquire
        watch_signal = self.immout.capture

        status = DeviceStatus(self)

        def closure(value, old_value, **kwargs):
            if value == done_value and old_value != value:
                watch_signal.clear_sub(closure)
                print("closure() method ends")
                print(f"cam.acquire.value={self.cam.acquire.value}")
                print(f"immout.capture.value={self.immout.capture.value}")
                print(f"immout.num_captured.value={self.immout.num_captured.value}")
                status._finished()
                print(f"status={status}")
        
        watch_signal.subscribe(closure)
        self.immout.capture.put(1, wait=False)
        acquire_signal.put(start_value, wait=False)
        return status

    # def trigger(self):    # default trigger method
    #     """Start acquisition"""
    #     signals = self.trigger_signals
    #     if len(signals) > 1:
    #         raise NotImplementedError('More than one trigger signal is not '
    #                                   'currently supported')
    #     status = DeviceStatus(self)
    #     if not signals:
    #         status._finished()
    #         return status

    #     acq_signal, = signals

    #     self.subscribe(status._finished,
    #                    event_type=self.SUB_ACQ_DONE, run=False)

    #     def done_acquisition(**ignored_kwargs):
    #         # Keyword arguments are ignored here from the EpicsSignal
    #         # subscription, as the important part is that the put completion
    #         # has finished
    #         self._done_acquiring()

    #     acq_signal.put(1, wait=False, callback=done_acquisition)
    #     return status
    
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
        # logger.debug(f"staging_setup_DM({args})")

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
