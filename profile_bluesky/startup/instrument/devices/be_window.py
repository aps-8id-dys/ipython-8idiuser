
"""
Beryllium Window 8-ID-I
"""

__all__ = ['bewindow',]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor

class BeWindow(Device):  
    """
    Beryllium Window 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:m17', labels=["motor", "optics"])
    z = Component(EpicsMotor, '8idi:m11', labels=["motor", "optics"])


bewindow = BeWindow(name="bewindow")
