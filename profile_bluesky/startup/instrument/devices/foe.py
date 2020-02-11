
"""
FOE: First Optical Enclosure
"""

__all__ = ['foepinhole', 'foemirror', 'WBslit']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class FOEpinholeDevice(Device):  
    """
    Optics Table 1 in 8-ID-A which holds the 270 um pin hole for heat load reduction
    """    
    x = Component(EpicsMotor, '8ida:TA1:x', labels=["motor", "table"]) 
    z = Component(EpicsMotor, '8ida:TA1:y', labels=["motor", "table"])
  

class FOEmirrorDevice(Device):  
    """
    Optics Table 2 in 8-ID-A which holds the First optical element Mirror
    """    
    x = Component(EpicsMotor, '8ida:TA2:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8ida:TA2:y', labels=["motor", "table"])
    theta = Component(EpicsMotor, '8ida:sm9', labels=["motor", "table"])


class WBslitDevice(Device):  
    """
    White Beam Slit in 8-ID-A
    """
    vgap = Component(EpicsMotor, '8ida:Slit1Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8ida:Slit1Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8ida:Slit1Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8ida:Slit1Hcenter', labels=["motor", "slit"])
    zu = Component(EpicsMotor, '8ida:m11', labels=["motor", "slit"])    
    xu = Component(EpicsMotor, '8ida:m14', labels=["motor", "slit"])    
    zd = Component(EpicsMotor, '8ida:m15', labels=["motor", "slit"])
    xd = Component(EpicsMotor, '8ida:m16', labels=["motor", "slit"])


foepinhole = FOEpinholeDevice(name="foepinhole")
foemirror = FOEmirrorDevice(name="foemirror")
WBslit = WBslitDevice(name="WBslit")
