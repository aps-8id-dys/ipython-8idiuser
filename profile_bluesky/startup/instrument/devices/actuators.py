
"""
actuators in 8-ID-I
"""

__all__ = [
    'actuator_pind1',
    'actuator_pind2',
    'actuator_flux',
]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import EpicsSignal

actuator_pind1 = EpicsSignal('8idi:9440:1:bo_2', name='actuator_pind1', labels=("actuator",))
actuator_pind2 = EpicsSignal('8idi:9440:1:bo_1', name='actuator_pind2', labels=("actuator",))
actuator_flux = EpicsSignal('8idi:9440:1:bo_0', name='actuator_flux', labels=("actuator",))
