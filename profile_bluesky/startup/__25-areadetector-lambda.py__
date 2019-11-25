logger.info(__file__)

"""area detector: X-Spectrum Lambda 750K"""

# from ophyd.device import Staged

# LAMBDA_750K_IOC_PREFIX = "8LAMBDA1:"

# DATABROKER_ROOT_PATH = "/"
# # AD_HDF5_IOC_WRITE_PATH = "/tmp/ADlambda/%Y/%m/%d/"     # FIXME: where will data be saved?
# AD_HDF5_IOC_WRITE_PATH = "/home/8-id-i/bluesky-AD-data/%Y/%m/%d/"
# AD_HDF5_DB_READ_PATH = AD_HDF5_IOC_WRITE_PATH


# class Lambda750kCam(CamBase):
#     """support for X-Spectrum Lambda 750K detector"""
#     _html_docs = []
#     config_file_path = Component(EpicsSignal, 'ConfigFilePath')
#     firmware_version = Component(EpicsSignalRO, 'FirmwareVersion_RBV')
#     operating_mode = Component(EpicsSignalWithRBV, 'OperatingMode')
#     serial_number = Component(EpicsSignalRO, 'SerialNumber_RBV')
#     temperature = Component(EpicsSignalWithRBV, 'Temperature')


# class ImmJoinPlugin(ADBase):
#     """plugin (not in ophyd)"""
#     capture_imm0 = Component(EpicsSignal, 'IMMFanoutCapture.OUTA')
#     capture_imm1 = Component(EpicsSignal, 'IMMFanoutCapture.OUTB')
#     capture_imm2 = Component(EpicsSignal, 'IMMFanoutCapture.OUTC')
#     joined_capture = Component(EpicsSignal, 'IMMJoinedCapture')


# class IMMFilePlugin(FilePlugin):
#     """plugin (not in ophyd)"""
#     _default_suffix = ''
#     _html_docs = ['NDFileIMM.html']
#     _plugin_type = 'NDFileIMM'
    
#     file_number_sync = None
#     file_number_write = None

#     imm_elapsed = Component(EpicsSignalRO, 'NDFileIMM_imm_elapsed_RBV')
#     is_already_imm = Component(EpicsSignalRO, 'NDFileIMM_is_already_imm_RBV')
#     imm_systicks = Component(EpicsSignalRO, 'NDFileIMM_imm_systicks_RBV')
#     imm_corecoticks = Component(EpicsSignalRO, 'NDFileIMM_imm_corecoticks_RBV')
#     imm_dlen = Component(EpicsSignalRO, 'NDFileIMM_imm_dlen_RBV')
#     threshold = Component(EpicsSignalWithRBV, 'NDFileIMM_threshold')
#     is_imm_comp = Component(EpicsSignalRO, 'NDFileIMM_is_imm_comp_RBV')
#     timestamp = Component(EpicsSignalRO, 'NDFileIMM_timestamp_RBV')
#     number_imm_pixels = Component(EpicsSignalRO, 'NDFileIMM_num_imm_pixels_RBV')

#     #  These records control file I/O
#     file_format = Component(EpicsSignalWithRBV, 'NDFileIMM_format')
#     unique_id = Component(EpicsSignalRO, 'NDFileIMM_uniqueID_RBV')
#     print_attributes = Component(EpicsSignal, 'NDFileIMM_printAttributes')
#     number_missed_timestamps = Component(EpicsSignalWithRBV, 'NDFileIMM_NmissedTimeStamps')
#     number_missed_ids = Component(EpicsSignalWithRBV, 'NDFileIMM_NmissedIDs')
#     number_img_rst_ts = Component(EpicsSignalWithRBV, 'NDFileIMM_Nimg_rst_ts')
#     throw_images = Component(EpicsSignalWithRBV, 'NDFileIMM_throw_images')
#     frame_period = Component(EpicsSignalWithRBV, 'NDFileIMM_framePeriod')
#     file_event = Component(EpicsSignalRO, 'NDFileIMM_fileevent')


# class GatherPlugin(PluginBase):
#     """plugin (override what is new in ophyd for now)"""
#     _default_suffix = 'GATHER1:'
#     _html_docs = ['gather.html']
#     _plugin_type = 'NDPluginGather'

# class ScatterPlugin(PluginBase):
#     """plugin (override what is new in ophyd for now)"""
#     _default_suffix = 'SCATTER1:'
#     _html_docs = ['scatter.html']
#     _plugin_type = 'NDPluginScatter'


# # Use one of these plugins when configuring the HDF support:
# #    Plugin_HDF5_Bluesky_Names  : Bluesky picks HDF5 file names, compatible with databroker
# #    Plugin_HDF5_EPICS_Names    : EPICS user picks HDF5 file names, not compatible with databroker

# class Plugin_HDF5_Bluesky_Names(
#     HDF5Plugin, 
#     FileStoreHDF5IterativeWrite
#     ):
#     create_directory_depth = Component(
#         EpicsSignalWithRBV, 
#         suffix="CreateDirectory")


# class EpicsHdf5IterativeWriter(
#     APS_devices.AD_EpicsHdf5FileName, # <-- code that uses EPICS naming
#     FileStoreIterativeWrite
#     ): pass
# class Plugin_HDF5_EPICS_Names(
#     HDF5Plugin, 
#     EpicsHdf5IterativeWriter  # <-- custom from above
#     ):
#     create_directory_depth = Component(
#         EpicsSignalWithRBV, 
#         suffix="CreateDirectory")


# class IMMOutTriggerStatus(DeviceStatus):
#     """
#     following ADTriggerStatus, this is for IMMOut plugin

#     A special status object that notifies watches (progress bars)
#     based on comparing device.immout.array_counter to  device.immout.num_captured.
#     """
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.start_ts = time.time()

#         # Notify watchers (things like progress bars) of new values
#         # at the device's natural update rate.
#         if not self.done:
#             self.device.immout.array_counter.subscribe(self._notify_watchers)
#             # some state needed only by self._notify_watchers
#             self._name = self.device.name
#             self._initial_count = self.device.immout.array_counter.get()
#             self._target_count = self.device.immout.num_captured.get()

#     def watch(self, func):
#         self._watchers.append(func)

#     def _notify_watchers(self, value, *args, **kwargs):
#         # *args and **kwargs catch extra inputs from pyepics, not needed here
#         if self.done:
#             self.device.immout.array_counter.clear_sub(self._notify_watchers)
#         if not self._watchers:
#             return
#         # Always start progress bar at 0 regardless of starting value of
#         # array_counter.
#         current = value - self._initial_count
#         target = self._target_count
#         initial = 0
#         time_elapsed = time.time() - self.start_ts
#         try:
#             fraction = (current - initial) / (target - initial)
#         except ZeroDivisionError:
#             fraction = 1
#         except Exception as exc:
#             fraction = None
#             time_remaining = None
#         else:
#             time_remaining = time_elapsed / fraction
#         for watcher in self._watchers:
#             watcher(name=self._name,
#                     current=current,
#                     initial=initial,
#                     target=target,
#                     unit='images',
#                     precision=0,
#                     fraction=fraction,
#                     time_elapsed=time_elapsed,
#                     time_remaining=time_remaining)


# class Lambda750kAreaDetector(SingleTrigger, AreaDetector): 
#     cam = ADComponent(Lambda750kCam, "cam1:")
#     image = Component(ImagePlugin, suffix="image1:")
#     #hdf1 = Component(
#     #    Plugin_HDF5_EPICS_Names,
#     #    suffix='HDF1:', 
#     #    root = DATABROKER_ROOT_PATH,
#     #    write_path_template = AD_HDF5_IOC_WRITE_PATH,
#     #    read_path_template = AD_HDF5_DB_READ_PATH,
#     #)
#     immjoin = Component(ImmJoinPlugin, "IMMJoin:")
#     imm0 = Component(IMMFilePlugin, "IMM0:")
#     imm1 = Component(IMMFilePlugin, "IMM1:")
#     imm2 = Component(IMMFilePlugin, "IMM2:")
#     imm3 = Component(IMMFilePlugin, "IMM3:")
#     immout = Component(IMMFilePlugin, "IMMout:")
#     gather = Component(GatherPlugin, "Gather1:")
#     scatter = Component(ScatterPlugin, "Scatter1:")

#     _status_type = IMMOutTriggerStatus  # our custom status

#     detector_number = 25    # 8-ID-I numbering of this detector
    
#     @property
#     def plugin_file_name(self):
#         """
#         return the file name the plugin wrote
        
#         Implement for the DM workflow.
#         """
#         # cut the path from file name
#         return os.path.basename(self.immout.full_file_name.value)
    
#     @property
#     def images_received(self):
#         return self.immout.num_captured.get()
    
#     def staging_setup_DM(self, *args, **kwargs):
#         """
#         setup the detector's stage_sigs for acquisition with the DM workflow
        
#         Implement this method in _any_ Device that requires custom
#         setup for the DM workflow.
#         """
#         if len(args) != 5:
#             raise IndexError(f"expected 5 parameters, received {len(args)}: args={args}")
#         file_path = args[0]
#         file_name = args[1]
#         num_images = args[2]
#         acquire_time = args[3]
#         acquire_period = args[4]

#         self.cam.stage_sigs["num_images"] = num_images
#         self.cam.stage_sigs["acquire_time"] = acquire_time
#         self.cam.stage_sigs["acquire_period"] = acquire_period
#         self.immout.stage_sigs["enable"] = 1
#         self.immout.stage_sigs["blocking_callbacks"] = "Yes"
#         self.immout.stage_sigs["parent.cam.array_callbacks"] = 1
#         self.immout.stage_sigs["file_path"] = file_path
#         self.immout.stage_sigs["file_name"] = file_name
#         self.immout.stage_sigs["num_capture"] = num_images
#         self.immout.stage_sigs["file_number"] = 1
#         self.immout.stage_sigs["file_format"] = "IMM_Cmprs"
#         self.immout.stage_sigs["capture"] = 1

#     # FIXME: acquisition stops when cam.acquire goes from 1 to 0
#     # # ophyd.areadetector.trigger_mixins.SingleTrigger().trigger()
#     # def trigger(self):
#     #     """
#     #     Trigger one acquisition

#     #     Custom trigger to wait for IMMout plugin to finish
#     #     in addition to waiting for CAM1 plugin
#     #     (array_counter  &  num_images)
#     #     """
#     #     if self._staged != Staged.yes:
#     #         raise RuntimeError("This detector is not ready to trigger."
#     #                            "Call the stage() method before triggering.")

#     #     # trigger_mixins.ADTriggerStatus
#     #     # compares device.cam.  array_counter  &  num_images
#     #     self._status = self._status_type(self)

#     #     def closure(value,old_value,**kwargs):
#     #         if value == 0 and old_value != value:
#     #             self.immout.capture.clear_sub(closure)
#     #             print("closure ends")
#     #             print(f"cam.acquire.value={self.cam.acquire.value}")
#     #             print(f"immout.capture.value={self.immout.capture.value}")
        
#     #     self.immout.capture.subscribe(closure)
#     #     self._acquisition_signal.put(1, wait=False)
#     #     self.dispatch(self._image_name, time.time())
#     #     return self._status


# try:
#     adlambda = Lambda750kAreaDetector(
#         LAMBDA_750K_IOC_PREFIX, 
#         name='adlambda',
#         labels=["areadetector",]
#         )

#     adlambda.read_attrs += "immjoin imm0 imm1 imm2 imm3 immout gather scatter".split()
#     #adlambda.read_attrs.append("hdf1")
#     # suggestions for setting HDF5 plugin defaults
#     # adlambda.hdf1.file_path.put(AD_HDF5_IOC_WRITE_PATH)
#     # adlambda.hdf1.file_name.put("bluesky")
#     # adlambda.hdf1.file_number.put(101)
#     # adlambda.hdf1.array_counter.put(adlambda.hdf1.file_number.value)
    
# except TimeoutError:
#     m = "Could not connect Lambda 750K detector"
#     m += f" with prefix  {LAMBDA_750K_IOC_PREFIX}"
#     logger.warning(m)
