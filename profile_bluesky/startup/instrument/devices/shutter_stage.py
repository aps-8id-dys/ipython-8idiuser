
"""
Shutter Stage
"""

__all__ = ['shutterstage',]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class ShutterStage(Device):  
    """
    Shutter Stage at 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:m1', labels=["motor", "shutter"])
    z = Component(EpicsMotor, '8idi:m2', labels=["motor", "shutter"])


shutterstage = ShutterStage(name="shutterstage")
