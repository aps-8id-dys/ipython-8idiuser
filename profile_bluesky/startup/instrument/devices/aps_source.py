
"""
APS only: connect with facility information
"""
 
__all__ = [
    'aps', 
    'undulator',
    ]

from ..session_logs import logger
logger.info(__file__)

import apstools.devices
from ophyd import Device, Component, Signal

from ..framework import sd


aps = apstools.devices.ApsMachineParametersDevice(name="aps")
try:
    aps.wait_for_connection(timeout=5.0)
except TimeoutError:
    cycle=aps.aps_cycle.get()
    class SimulatedAPSDevice(Device):
        aps_cycle = Component(Signal, value=cycle)
        inUserOperations=Component(Signal, value=False)
        current=Component(Signal, value=0.0)
    aps=SimulatedAPSDevice(name='aps')

    logger.warning('Simulated APS device for testing during non-operation weeks')

sd.baseline.append(aps)

undulator = apstools.devices.ApsUndulatorDual("ID08", name="undulator")
try:
    undulator.wait_for_connection(timeout=5.0)
except TimeoutError:
    class SimulatedUndulatorDevice(Device):
        simulator = Component(Signal, value=True)
    undulator=SimulatedUndulatorDevice(name='undulator')

sd.baseline.append(undulator)
