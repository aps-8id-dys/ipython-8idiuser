
"""
Sample Stage components
"""

__all__ = ['samplestage',]

from instrument.session_logs import logger
logger.info(__file__)

from instrument.devices.data_management import dm_pars
from instrument.startup import bps
import numpy as np
from ophyd import Component, Device, EpicsMotor



#class SamplePiezo(Device):  
#    """
#    Piezo stage at the sample?
#    """    
#    x = Component(EpicsMotor, '8idi:m69', labels=["motor", "sample"])
#    z = Component(EpicsMotor, '8idi:m70', labels=["motor", "sample"])


class SampleStageTable(Device):
    """
    Sample stage table TI-3
    """
    x = Component(EpicsMotor, '8idi:TI3:x', labels=["motor", "table", "sample"])
    y = Component(EpicsMotor, '8idi:TI3:z', labels=["motor", "table", "sample"])
    z = Component(EpicsMotor, '8idi:TI3:y', labels=["motor", "table", "sample"])


class SampleStage(Device):
    """
    Sample stage

    To change the x & z positions for movesample(),
    redefine the xdata & zdata numpy arrays.  It's easy and direct.

        samplestage.xdata = np.linspace(0, 2, 21)    # runs from 0 to 2 with 21 points
        samplestage.zdata = np.linspace(0, .5, 15)   # runs from 0 to 0.5 with 15 points

    """
    x = Component(EpicsMotor, '8idi:m54', labels=["motor", "sample"])
    y = Component(EpicsMotor, '8idi:m49', labels=["motor", "sample"])
    z = Component(EpicsMotor, '8idi:m50', labels=["motor", "sample"])
    phi = Component(EpicsMotor, '8idi:m51', labels=["motor", "sample"])     # yaw
    theta = Component(EpicsMotor, '8idi:m52', labels=["motor", "sample"])   # pitch
    chi = Component(EpicsMotor, '8idi:m53', labels=["motor", "sample"])     # roll
    table = Component(SampleStageTable, labels=["table",])

    # used by the movesample plans
    nextpos = 0
    xdata = np.linspace(0, 2, 21)    # example: user will change this
    zdata = np.linspace(0, .5, 15)    # example: user will change this

    def movesample(self):
        """
        move the sample x&z to the next position
        """
        if dm_pars.geometry_num.get() == 0: # transmission
            xn = len(self.xdata)
            zn = len(self.zdata)
            if xn > zn:
                x = self.nextpos % xn
                z = int(self.nextpos/xn) % zn
            else:
                x = int(self.nextpos/zn) % xn
                z = self.nextpos % zn
        else:    # reflection
            x = self.nextpos % len(self.xdata)
            z = self.nextpos % len(self.zdata)

        x = self.xdata[x]
        z = self.zdata[z]
        logger.info(f"Moving samx to {x}, samz to {z}")
        yield from bps.mv(
            self.x, x,
            self.z, z,
            )
        self.nextpos += 1

    def movesamx(self):
        index = self.nextpos % len(self.xdata)
        p = self.xdata[index]
        logger.info(f"Moving samx to {p}")
        yield from bps.mv(self.x, p)
        self.nextpos += 1

    def movesamz(self):
        index = self.nextpos % len(self.zdata)
        p = self.zdata[index]
        logger.info(f"Moving samz to {p}")
        yield from bps.mv(self.z, p)
        self.nextpos += 1


samplestage = SampleStage(name="samplestage")
