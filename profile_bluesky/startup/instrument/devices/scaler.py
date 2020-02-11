
"""
detectors (area detectors handled separately)
"""

__all__ = [
    'scaler',
    'clock',
    'I0',
    'scint',
    'diode',
    'I0Mon',
    'ROI1',
    'ROI2'
]

from ophyd.scaler import ScalerCH
from ..session_logs import logger
logger.info(__file__)


scaler = ScalerCH('sky:scaler1', name='scaler', labels=("detectors",))

if len(scaler.channels.chan01.chname.value) == 0:
    scaler.channels.chan01.chname.put("clock")
    scaler.channels.chan02.chname.put("I0")
    scaler.channels.chan03.chname.put("scint")
    scaler.channels.chan05.chname.put("diode")
    scaler.channels.chan08.chname.put("I0Mon")
    scaler.channels.chan10.chname.put("ROI1")
    scaler.channels.chan11.chname.put("ROI2")
scaler.select_channels(None)

# name some channels for convenience
clock = scaler.channels.chan01.s
I0 = scaler.channels.chan02.s
scint = scaler.channels.chan03.s
diode = scaler.channels.chan05.s
I0Mon = scaler.channels.chan08.s
ROI1 = scaler.channels.chan10.s
ROI2 = scaler.channels.chan11.s

for obj in (clock, I0, scint, diode, I0Mon, ROI1, ROI2):
    obj._ophyd_labels_ = set(list(obj._ophyd_labels_) + ["counter"])
