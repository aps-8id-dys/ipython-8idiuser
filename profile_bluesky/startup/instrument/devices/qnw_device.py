
# This is the definition file for the qnw temperature controller

from .util_components import PVPositionerSoftDone
from ophyd import EpicsSignal, EpicsSignalRO, Signal, Component

__all__ = "qnw_env1 qnw_env2 qnw_env3".split()

class QnwDevice(PVPositionerSoftDone):

    readback = Component(EpicsSignalRO, "SH_RBV", kind="hinted", auto_monitor=True)
    setpoint = Component(EpicsSignal, "TARG", kind="normal", put_complete=True)
    tolerance = Component(Signal, value=0.1, kind="config")    

qnw_env1 = QnwDevice("8idi:QNWenv_1:", name="qnw_env1")
qnw_env2 = QnwDevice("8idi:QNWenv_2:", name="qnw_env2")
qnw_env3 = QnwDevice("8idi:QNWenv_3:", name="qnw_env3")


# TO-DO:
# Add ramp;
# Add read-only temperatures to watch;
# Figure out how to change temperature and wait while blocking next command
# Overwrite STOP feature (pause the course; take the read-back temperature and write to the set point)