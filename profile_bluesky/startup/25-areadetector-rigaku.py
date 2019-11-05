logger.info(__file__)

"""detector: Rigaku (not EPICS area detector though)"""


class UnixCommandSignal(Signal):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.unix_command = None
        self.unix_output = None
        self.unix_error = None
        self.process = None

    def set(self, unix_command):
        status = DeviceStatus(self)
        self.unix_command = unix_command
        self.process = subprocess.Popen(
            unix_command, 
            shell=True,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            )

        @APS_utils.run_in_thread
        def closure():
            self.unix_output, self.unix_error = self.process.communicate()
            status._finished()

        closure()    
        return status

    def put(self, unix_command):
        status = self.set(unix_command)
        while not status.done:
            time.sleep(0.01)

    def get(self):
        return self.unix_output, self.unix_error


class Rigaku_8IDI(Device):
    """
    Supports non-epics communication with the new Rigaku detector

    How to use:
    
    1. R1 = Rigaku_8IDI(name = 'R1')
    2. yield from bps.mv(R1.batch_name, 'A001_Test')
    3. yield from bps.count([R1])
    """
    qmap_file = "qzhang1026_rerun_minus_streak.h5"

    acquire_start = Component(EpicsSignal, "8idi:Unidig2Bo7.VAL")
    acquire_complete = Component(EpicsSignalRO, "8idi:Unidig2Bi2.VAL") 

    unix_process = Component(UnixCommandSignal)

    batch_name = Component(Signal, value="A001")

    detector_number = 46    # 8-ID-I numbering of this detector

    def stage(self):
        shutter_mode.put("UFXC")    # data mode
        shutter_control.put("Open")
        shutter_override.put("High")
        cmd = f"echo FILE:F:{self.batch_name.value} | nc rigaku1.xray.aps.anl.gov 10000"
        self.unix_process.put(cmd)
    
    # TODO: unstage? do we need/want a custom method?
    #         shutter_mode.put("1UFXC") "align" mode for any detector


    def trigger(self):
        self.acquire_start.put(0)
        status = DeviceStatus(self)

        def closure(value,old_value,**kwargs):
            if value == 1 and old_value == 0:
                self.acquire_start.put(0)
                status._finished()

        self.acquire_complete.subscribe(closure)
        self.acquire_start.put(1)
        return status
    
    @property
    def plugin_file_name(self):
        return f"{self.batch_name.value}.bin"
    
    @property
    def images_received(self):
        """Rigaku tells us not to change this.  100k images every time."""
        return 100000
    
    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the detector's stage_sigs for acquisition with the DM workflow
        
        Implement this method in _any_ Device that requires custom
        setup for the DM workflow.
        """
        if len(args) != 5:
            raise IndexError(f"expected 5 parameters, received {len(args)}: args={args}")
        # file_path = args[0]
        file_name = args[1]
        # num_images = args[2]
        # acquire_time = args[3]
        # acquire_period = args[4]

        self.batch_name.put(file_name)

try:
    rigaku = Rigaku_8IDI(name="rigaku", labels=["rigaku",])
except TimeoutError:
    m = "Could not connect Rigaku detector"
    logger.warning(m)
