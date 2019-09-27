logger.info(__file__)

"""detector: Rigaku (not EPICS area detectorm though)"""


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

    shutter_control = Component(EpicsSignal, "8idi:softGlueC:AND-4_IN2_Signal")
    acquire_start = Component(EpicsSignal, "8idi:Unidig2Bo7.VAL")
    acquire_complete = Component(EpicsSignalRO, "8idi:Unidig2Bi2.VAL") 

    unix_process = Component(UnixCommandSignal)

    batch_name = Component(Signal, value=None)

    def stage(self):
        cmd = f"echo FILE:F:{self.batch_name.value} | nc rigaku1.xray.aps.anl.gov 10000"
        self.unix_process.put(cmd)

    def trigger(self):
        self.acquire_start.put(1)
        status = DeviceStatus(self)

        def closure(value,old_value,**kwargs):
            if value == 1 and old_value == 0:
                self.acquire_start.put(0)
                status._finished()

        self.acquire_complete.subscribe(closure)
        return status
    
    # @property
    # def plugin_file_name(self):
    #     # cut the path from file name
    #     return os.path.basename(self.immout.full_file_name.value)
    
    # @property
    # def images_received(self):
    #     return self.immout.num_captured.get()
    
    # def staging_setup_DM(self, *args, **kwargs):
    #     pass
