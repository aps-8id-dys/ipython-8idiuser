logger.info(__file__)

"""local, custom Device definitions"""


class CompoundRefractiveLensDevice(Device):
    x = Component(EpicsMotor, '8idi:m65', labels=["motor", "crl", "optics"])
    # y = Component(EpicsMotor, '8idi:m68', labels=["motor", "crl", "optics"])
    z = Component(EpicsMotor, '8idi:m62', labels=["motor", "crl", "optics"])
    pitch = Component(EpicsMotor, '8idi:m67', labels=["motor", "crl", "optics"])
    yaw = Component(EpicsMotor, '8idi:m66', labels=["motor", "crl", "optics"])


class MonochromatorDevice(Device):
    energy = Component(EpicsMotor, '8idimono:sm2', labels=["motor", "mono", "optics"])
    theta = Component(EpicsMotor, '8idimono:sm1', labels=["motor", "mono", "optics"])
    piezo = Component(EpicsMotor, '8idimono:m4', labels=["motor", "mono", "optics"])
    pico = Component(EpicsMotor, '8idimono:m1', labels=["motor", "mono", "optics"])
    nano = Component(EpicsMotor, '8idimono:m5', labels=["motor", "mono", "optics"])


class SlitA1Device(Device):  
    """
    Slit1 in 8-ID-A
    """
    vgap = Component(EpicsMotor, '8ida:Slit1Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8ida:Slit1Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8ida:Slit1Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8ida:Slit1Hcenter', labels=["motor", "slit"])
    zu = Component(EpicsMotor, '8ida:m11', labels=["motor", "slit"])    
    xu = Component(EpicsMotor, '8ida:m14', labels=["motor", "slit"])    
    zd = Component(EpicsMotor, '8ida:m15', labels=["motor", "slit"])
    xd = Component(EpicsMotor, '8ida:m16', labels=["motor", "slit"])


class SlitI1Device(Device):  
    """
    Slit1 in 8-ID-I
    """
    x = Component(EpicsMotor, '8idi:m18', labels=["motor", "slit"])
    vgap = Component(EpicsMotor, '8idi:Slit1Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit1Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit1Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit1Hcenter', labels=["motor", "slit"])


class SlitI2Device(Device):  
    """
    Slit2 in 8-ID-I
    """
    vgap = Component(EpicsMotor, '8idi:Slit2Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit2Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit2Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit2Hcenter', labels=["motor", "slit"])    


class SlitI3Device(Device):  
    """
    Slit3 in 8-ID-I
    """
    vgap = Component(EpicsMotor, '8idi:Slit3Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit3Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit3Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit3Hcenter', labels=["motor", "slit"])    


class SlitI4Device(Device):  
    """
    Slit4 in 8-ID-I
    """
    vgap = Component(EpicsMotor, '8idi:Slit4Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit4Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit4Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit4Hcenter', labels=["motor", "slit"])    


class SlitI5Device(Device):  
    """
    Slit5 in 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:m55', labels=["motor", "slit"])
    z = Component(EpicsMotor, '8idi:m56', labels=["motor", "slit"])
    vgap = Component(EpicsMotor, '8idi:Slit5Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit5Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit5Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit5Hcenter', labels=["motor", "slit"])


class SlitIpinkDevice(Device):  
    """
    Slitpink in 8-ID-I
    """    
    vgap = Component(EpicsMotor, '8idi:SlitpinkVsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:SlitpinkVcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:SlitpinkHsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:SlitpinkHcenter', labels=["motor", "slit"])


class LS336_Loop(APS_devices.ProcessController):
    """
    One control loop on the LS336 temperature controller
    
    Each control loop is a separate process controller.
    """
    signal = FormattedComponent(EpicsSignalRO, "{self.prefix}OUT{self.loop_number}:SP_RBV")
    target = FormattedComponent(EpicsSignal, "{self.prefix}OUT{self.loop_number}:SP", kind="omitted")
    units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units", kind="omitted")

    loop_name = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}:Name_RBV")
    temperature = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}")

    control = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Cntrl")
    manual = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:MOUT")
    mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Mode")

    def __init__(self, *args, loop_number=None, **kwargs):
        self.controller_name = f"Lakeshore 336 Controller Loop {loop_number}"
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)


class LS336_LoopHeaterPidControls(LS336_Loop):
    """
    Additional controls for loop1 and loop2: heater and pid
    """
    # only on loops 1 & 2
    heater = FormattedComponent(EpicsSignalRO, "{self.prefix}HTR{self.loop_number}")
    heater_range = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}HTR{self.loop_number}:Range")

    pid_P = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}P{self.loop_number}")
    pid_I = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}I{self.loop_number}")
    pid_D = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}D{self.loop_number}")
    ramp_rate = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}RampR{self.loop_number}")
    ramp_on = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OnRamp{self.loop_number}")


class LS336Device(Device):
    """
    support for Lakeshore 336 temperature controller

    Basic set and read channels (there are 4 channels) and PID and ramping.
    This controller is a bit complicated as it has 1x 100W and 1x50W output. 
    
    Also, "{self.prefix}read" has the usual fields common to all records
    (.SCAN & .PROC are important)
    Also, the asyn record in "{self.prefix}serial" needs an interface.
    """
    # basic support for now
    # https://github.com/aps-8id-trr/ipython-8idiuser/issues/33
    loop1 = FormattedComponent(LS336_LoopHeaterPidControls, "{self.prefix}", loop_number="1")
    loop2 = FormattedComponent(LS336_LoopHeaterPidControls, "{self.prefix}", loop_number="2")
    loop3 = FormattedComponent(LS336_Loop, "{self.prefix}", loop_number="3")
    loop4 = FormattedComponent(LS336_Loop, "{self.prefix}", loop_number="4")
    
    # from apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN")
    process_record = Component(EpicsSignal, "read.PROC")
    
    read_all = Component(EpicsSignal, "readAll.PROC")
    
    # needed (not available) from apstools.synApps
    # serial = Component(AsynRecord, "serial")      # TODO:

    @property
    def value(self):
        """designate one loop as the default signal to return"""
        return self.loop1.signal
