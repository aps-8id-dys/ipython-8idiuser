
"""
Monochromator, and related components
"""

__all__ = ['monochromator', 'diamond']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class MonochromatorTableDevice(Device):
    """
    Table TI-1 in 8-ID-I
    """
    x = Component(EpicsMotor, '8idi:TI1:x', labels=["motor", "mono", "optics", "table"])
    z = Component(EpicsMotor, '8idi:TI1:y', labels=["motor", "mono", "optics", "table"])


class MonochromatorDevice(Device):
    energy = Component(EpicsMotor, '8idimono:sm2', labels=["motor", "mono", "optics"])
    theta = Component(EpicsMotor, '8idimono:sm1', labels=["motor", "mono", "optics"])
    piezo = Component(EpicsMotor, '8idimono:m4', labels=["motor", "mono", "optics"])
    pico = Component(EpicsMotor, '8idimono:m1', labels=["motor", "mono", "optics"])
    nano = Component(EpicsMotor, '8idimono:m5', labels=["motor", "mono", "optics"])
    table = Component(MonochromatorTableDevice, labels=["mono", "optics", "table"])


class BeamSplittingMonochromatorDevice(Device):  
    """
    I/E Beam-splitting Silicon monochromator in 8-ID-D
    """    
    x = Component(EpicsMotor, '8idd:m1', labels=["motor", "optics"])
    z = Component(EpicsMotor, '8idd:m2', labels=["motor", "optics"])


monochromator = MonochromatorDevice(name="monochromator")
diamond = BeamSplittingMonochromatorDevice(name="diamond")
