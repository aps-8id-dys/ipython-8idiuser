
"""
Tables: Optics and Flight Path
"""

__all__ = ['opticstable', 'flightpathtable']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class OpticsTable(Device):  
    """
    Optics Table 2 in 8-ID-I which holds optics and slits
    """    
    x = Component(EpicsMotor, '8idi:TI2:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8idi:TI2:y', labels=["motor", "table"])
   
 
class FlightPathTable(Device):  
    """
    Optics Table 4 in 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:TI4:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8idi:TI4:y', labels=["motor", "table"])
    zu = Component(EpicsMotor, '8idi:m30', labels=["motor", ])
    zdo = Component(EpicsMotor, '8idi:m31', labels=["motor", ])
    zdi = Component(EpicsMotor, '8idi:m32', labels=["motor", ])
    xu = Component(EpicsMotor, '8idi:m28', labels=["motor", ])
    xd = Component(EpicsMotor, '8idi:m29', labels=["motor", ])
 
 
opticstable = OpticsTable(name="opticstable")
flightpathtable = FlightPathTable(name="flightpathtable")
