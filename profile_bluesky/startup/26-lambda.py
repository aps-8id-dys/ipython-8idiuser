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

    bad_frame_counter = Component(EpicsSignal, 'BadFrameCounter', kind='config') 
    config_file_path = Component(EpicsSignal, 'ConfigFilePath', string=True, kind='config')
    data_type = Component(EpicsSignalWithRBV, 'DataType', kind='config')
    firmware_version = Component(EpicsSignalRO, 'FirmwareVersion_RBV', string=True, kind='config')
    image_mode = Component(EpicsSignalWithRBV, 'ImageMode', kind='config')
    operating_mode = Component(EpicsSignalWithRBV, 'OperatingMode', kind='config')
    serial_number = Component(EpicsSignalRO, 'SerialNumber_RBV', string=True, kind='config')
    temperature = Component(EpicsSignalWithRBV, 'Temperature', kind='config')
    trigger_mode = Component(EpicsSignalWithRBV, 'TriggerMode', kind='config')

    EXT_TRIGGER = 0

    # constants
    MODE_TRIGGER_INTERNAL = 0
    MODE_TRIGGER_EXTERNAL_PER_SEQUENCE = 1
    MODE_TRIGGER_EXTERNAL_PER_FRAME = 2
    MODE_MULTIPLE_IMAGE = 1

    @property
    def getBadFrameCount(self):
        """
        """
        # from SPEC macro: ccdget_Lambda_BadFrameCount
        return self.bad_frame_counter.value

    @property
    def getDataType(self):
        # from SPEC macro: ccdget_DataType_ad
        return self.data_type.value

    @property
    def getOperatingMode(self):
        return self.operating_mode.value

    def setDataType(self, value):
        """
        value: 0-7 for ('Int8', 'UInt8', 'Int16', 'UInt16', 'Int32', 'UInt32', 'Float32', 'Float64')
        """
        # from SPEC macro: ccdset_DataType_ad
        yield from bps.mv(self.self.data_type, value)

    def setImageMode(self, mode):
        """
        mode = 0, 1 for ('Single', 'Multiple')
        """
        # from SPEC macro: ccdset_ImageMode
        if mode not in (0, 1):
            msg = f"image mode {mode} not allowed, must be one of 0, 1"
            raise ValueError(msg)
        yield from bps.mv(self.image_mode, mode)

    def setOperatingMode(self, mode):
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
            yield from self.setDataType(3)     # 3: UInt16
            data_type = self.getDataType
            logger.info("Lambda DataType switched to: {data_type}")

    def setTime(self, exposure_time, exposure_period):
        """
        set exposure time and period
        """
        # from SPEC macro: ccdset_time_Lambda
        # set exp time always regardless of any mode
        yield from bps.mv(self.acquire_time, exposure_time)
        # yield from bps.sleep(0.05)

        # set period based on the mode
        if self.getOperatingMode == 0:      # continuous read/write mode
            yield from bps.mv(self.acquire_period, exposure_time)
        else:
            extra = 1e-3     # 1 ms is typical for period
            extra += 100e-6  # extra 100 us for 24-bit mode (empirical)
            yield from bps.mv(
                self.acquire_period, 
                max(exposure_period, exposure_time + extra)
                )
        # yield from bps.sleep(0.05)

        if self.EXT_TRIGGER > 0 and self.getOperatingMode == 0: 
            # this should work for single-trigger per sequence as well
            yield from bps.mv(pvDELAY_B, 1e-4)  # for softglue trigger generation (shorter than the fastest frame time)
            # yield from bps.sleep(0.05)
            yield from bps.mv(pvDELAY_A, exposure_time)  # AcquirePeriod in area detector
            # yield from bps.sleep(0.05)

        elif self.EXT_TRIGGER == 2 and self.getOperatingMode == 1:
            yield from bps.mv(pvDELAY_B, exposure_time)  # AcquireTime in area detector
            # yield from bps.sleep(0.05)
            yield from bps.mv(pvDELAY_A, exposure_time + 0.0011)  # AcquirePeriod in area detector
            # yield from bps.sleep(0.05)

        elif self.EXT_TRIGGER == 1 and self.getOperatingMode == 1:
            # important thing to be aware:
            # lambda does not support acquire_period in any way, 
            # except with trigger per frame mode
            yield from bps.mv(pvDELAY_B, exposure_time)  # AcquireTime in area detector
            # yield from bps.sleep(0.05)
            yield from bps.mv(pvDELAY_A, exposure_time + 0.0011)  # AcquirePeriod in area detector
            # yield from bps.sleep(0.05)

    def setTriggerMode(self, mode):
        """
        mode = 0,1,2 for Internal, External_per_sequence, External_per_frame
        note: mode = 3 ("Gating_Mode", permitted by EPICS record) is not supported here
        """
        # from SPEC macro: ccdset_TriggerMode_Lambda
        if mode not in (0, 1, 2):
            msg = f"trigger mode {mode} not allowed, must be one of 0, 1, 2"
            raise ValueError(msg)
        yield from bps.mv(self.trigger_mode, mode)

    def setup_modes(self, num_triggers):
        """
        set up modes accordingly, based on self.EXT_TRIGGER
        """
        # from SPEC macro: Lambda_modes_setup

        # FIXME: this looks like useless code
        # FIXME: we have no such self.LAMBDA_OPERATING_MODE now
        yield from self.setOperatingMode(self.LAMBDA_OPERATING_MODE)
        # if (LAMBDA_OPERATING_MODE == 1) { ##24-bit mode
        #     ccdset_OperatingMode_Lambda 1
        # } else { ##keep 12-bit ZDT as the default mode
        #     ccdset_OperatingMode_Lambda 0
        # }

        yield from self.setTriggerMode(self.EXT_TRIGGER)
        # TODO: shutteroff_default
        if self.EXT_TRIGGER == self.MODE_TRIGGER_EXTERNAL_PER_FRAME:
            action = "OPEN AND CLOSE DURING"
        else:   # self.MODE_TRIGGER_INTERNAL and self.MODE_TRIGGER_EXTERNAL_PER_SEQUENCE
            action = "REMAIN OPEN THROUGH"
        logger.info(f"Shutter will *{action}* the Acquisition...")

    def setup_trigger_logic_external(self, num_triggers):
        """
        configure the number of triggers to be expected
        """
        # from SPEC macro: external_trigger_logic_setup_Data_Lambda

        # Set number of frames in SGControl1 depending on the mode
        if self.getOperatingMode == 0:
            num_triggers += 1
        yield from bps.mv(sg_num_frames, num_triggers)

        yield from bps.mv(soft_glue.send_ext_pulse_tr_sig_to_trig, 1) # external trigger
        #####shutter burst/regular mode and the corresponding trigger pulses are selected separately###

    def setup_trigger_mode_external(self):
        """
        configure EPICS area detector for external triggering

        user can change chosen image mode via `self.EXT_TRIGGER`
        """
        # from SPEC macro: external_trigger_mode_setup_Lambda
        yield from self.setTriggerMode(self.EXT_TRIGGER)
        yield from self.setImageMode(self.MODE_MULTIPLE_IMAGE)

    def setup_trigger_mode_internal(self):
        """
        configure EPICS area detector for internal triggering, multiple images
        """
        # from SPEC macro: internal_trigger_mode_setup_Lambda
        yield from self.setTriggerMode(self.MODE_TRIGGER_INTERNAL)
        yield from self.setImageMode(self.MODE_MULTIPLE_IMAGE)


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
    # FIXME: TimeoutError: 8LAMBDA1:IMMout:FullFileName could not connect within 1.0-second timeout.
    full_file_name = Component(EpicsSignalRO, "FullFileName", string=True, kind='config')
    num_capture = Component(EpicsSignalWithRBV, "NumCapture", kind='config')
    num_captured = Component(EpicsSignalRO, "NumCaptured_RBV")
    num_pixels = Component(EpicsSignalWithRBV, "NDFileIMM_num_imm_pixels_RBV", kind='config')

    unique_id = Component(EpicsSignalRO, 'NDFileIMM_uniqueID_RBV')


class StatsLocal(Device):
    """
    local interface to the Stats plugin
    """

    # implement just the parts needed by our data acquisition
    mean_value = Component(EpicsSignalWithRBV, "MeanValue", kind='config')


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
    imm0 = Component(IMMoutLocal, "IMM0:")
    imm1 = Component(IMMoutLocal, "IMM1:")
    imm2 = Component(IMMoutLocal, "IMM2:")
    stats1 = Component(StatsLocal, "Stats1:")

    @property
    def chk_ccdc(self):
        """
        check if there is a pseudo counter "ccdc" configured in spec

        Look through all the counters and report if 
        any one of them is named `ccdc`.
        """
        # FIXME: We don't have a counter named "ccdc"
        return False

    @property
    def getCounts(self):
        """
        get counts from IMM plugins
        """
        # from SPEC macro: ccd_getcounts_ad_Lambda
        # FIXME: this routine needs attention

        # BUT, this is only used when there is a 
        # pseudo-counter named "ccdc" (that's what chk_ccdc() does)
        if self.chk_ccdc:
            if dm_pars.compression.value == 1:
                return self.immout.num_pixels.value
            else:
                return self.stats1.mean_value.value
    
    @property
    def images_received(self):
        return self.immout.num_captured.get()
    
    @property
    def plugin_file_name(self):
        """
        return the file name the plugin wrote
        
        Implement for the DM workflow.
        """
        # cut the path from file name
        return os.path.basename(self.immout.full_file_name.value)

    def setIMM_Cmprs(self):
        """
        set all IMM plugins for compression
        """
        # from SPEC macro: ccdset_compr_params_ad_Lambda
        for plugin in (self.imm0, self.imm1, self.imm2, self.immout):
            if plugin.file_format.value not in (1, 'IMM_Cmprs'):
                yield from bps.mv(
                    plugin.capture, 'Done',             # ('Done', 'Capture')
                    plugin.file_format, 'IMM_Cmprs',    # ('IMM_Raw', 'IMM_Cmprs')
                )

    def setIMM_Raw(self):
        """
        set all IMM plugins for raw (uncompressed)
        """
        # from SPEC macro: ccdset_RawMode_params_ad_Lambda
        for plugin in (self.imm0, self.imm1, self.imm2, self.immout):
            if plugin.file_format.value not in (0, 'IMM_Raw'):
                yield from bps.mv(
                    plugin.capture, 'Done',             # ('Done', 'Capture')
                    plugin.file_format, 'IMM_Raw',      # ('IMM_Raw', 'IMM_Cmprs')
                )

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
    
    def xpcs_loop(self, *args, **kwargs):
        """
        Combination of `xpcs_pre_start_LAMBDA` and `user_xpcs_loop_LAMBDA`

        see: https://github.com/aps-8id-trr/ipython-8idiuser/issues/107
        """
        pass    # TODO:


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
