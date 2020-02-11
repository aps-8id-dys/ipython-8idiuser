
"""
Slits
"""

__all__ = ['si1', 'si2', 'si3', 'si4', 'si5', 'sipink']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


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


si1 = SlitI1Device(name="si1")
si2 = SlitI2Device(name="si2")
si3 = SlitI3Device(name="si3")
si4 = SlitI4Device(name="si4")
si5 = SlitI5Device(name="si5")
sipink = SlitIpinkDevice(name="sipink")
