
"""
various motors
"""

__all__ = [
    'tth',
    'tth_act',
    'bstop',
    'alpha',
    'tthAPD',
    'foceye',
]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import EpicsMotor


tth = EpicsMotor('8idi:sm1', name='tth', labels=("motor",))

tth_act = EpicsMotor('8idi:m63', name='tth_act', labels=("motor",))
bstop = EpicsMotor('8idi:m27', name='bstop', labels=("motor",))
alpha = EpicsMotor('8idi:sm2', name='alpha', labels=("motor",))
tthAPD = EpicsMotor('8idi:sm3', name='tthAPD', labels=("motor",))
foceye = EpicsMotor('8idi:m37', name='foceye', labels=("motor",))
