
"""
Attenuators
"""

__all__ = ['att1', 'att2', 'Atten1', 'Atten2', 'att']

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import EpicsSignal, EpicsSignalRO

Atten1 = EpicsSignalRO('8idi:userTran1.P', name='Atten1', labels=["detectors",])
Atten2 = EpicsSignalRO('8idi:userTran3.P', name='Atten2', labels=["detectors",])
att1 = EpicsSignal('8idi:BioDecode1.A', name='att1', write_pv='8idi:BioEncode1.A')
att2 = EpicsSignal('8idi:BioDecode2.A', name='att2', write_pv='8idi:BioEncode2.A')

# att will be defined to be att1 or att2 based on the ops for the week
att = att2 
