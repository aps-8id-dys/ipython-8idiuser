logger.info(__file__)

"""X-Spectrum Lambda 750K (not `ophyd.areaDetector`)"""

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
    trigger_mode = Component(EpicsSignalWithRBV, 'TriggerMode', kind='config')

    def set_TriggerMode(self, mode):
        """
        mode = 0,1,2 for Internal, External_per_sequence, External_per_frame
        note: mode = 3 ("Gating_Mode", permitted by EPICS record) is not supported here
        """
        # from SPEC macro: ccdset_TriggerMode_Lambda
        if mode not in (0, 1, 2):
            msg = f"trigger mode {mode} not allowed, must be one of 0, 1, 2"
            raise ValueError(msg)
        yield from bps.mv(self.trigger_mode, mode)

    def set_OperatingMode(self, mode):
        """
        mode = 0, 1 for ContinuousReadWrite(12-bit), TwentyFourBit
        """
        # from SPEC macro: ccdset_OperatingMode_Lambda
        if mode not in (0, 1):
            msg = f"operating mode {mode} not allowed, must be one of 0, 1"
            raise ValueError(msg)
        if self.operating_mode.value != mode:
            yield from bps.mv(self.operating_mode, mode)
            # yield from bps.sleep(5.0)     # TODO: still needed?
            logger.info(f"Lambda Operating Mode switched to: {mode}")

        if self.operating_mode.value == 1:
            yield from self.set_DataType(3)     # TODO: What does 3 mean?
            data_type = self.get_DataType
            logger.info("Lambda DataType switched to: {data_type}")

    @property
    def get_DataType(self, value):
        """
        ???
        """
        # from SPEC macro: ccdget_DataType_ad
        raise NotImplementedError("Need to translate SPEC macro: ccdget_DataType_ad")

    def set_DataType(self, value):
        """
        value = ??? 3 means ???
        """
        # from SPEC macro: ccdset_DataType_ad
        # yield from bps.mv(self.some_signal, value)
        raise NotImplementedError("Need to translate SPEC macro: ccdset_DataType_ad")


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
    qmap_file = "Lambda_qmap.h5"

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
    
    def xpcs_loop(self, *args, **kwargs):
        """
        Combination of `xpcs_pre_start_LAMBDA` and `user_xpcs_loop_LAMBDA`

        see: https://github.com/aps-8id-trr/ipython-8idiuser/issues/107
        """
        pass    # TODO:
    
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
