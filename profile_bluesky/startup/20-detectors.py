logger.info(__file__)

"""detectors (area detectors handled separately)"""

scaler1 = ScalerCH('8idi:scaler1', name='scaler1', labels=["scalers", "detectors"])
scaler1.select_channels(None)   # choose just the channels with EPICS names

# This configuration moved from 15-spec-config.py
# counter: sec = SpecCounter(mne='sec', config_line='0', name='Seconds', unit='0', chan='0', pvname=8idi:scaler1.S1)
# counter: pind1 = SpecCounter(mne='pind1', config_line='1', name='pind1', unit='0', chan='1', pvname=8idi:scaler1.S2)
# counter: I0Mon = SpecCounter(mne='I0Mon', config_line='2', name='I0Mon', unit='0', chan='7', pvname=8idi:scaler1.S8)
# counter: pind2 = SpecCounter(mne='pind2', config_line='3', name='pind2', unit='0', chan='2', pvname=8idi:scaler1.S3)
# counter: pind3 = SpecCounter(mne='pind3', config_line='4', name='pind3', unit='0', chan='3', pvname=8idi:scaler1.S4)
# counter: pind4 = SpecCounter(mne='pind4', config_line='5', name='pind4', unit='0', chan='4', pvname=8idi:scaler1.S5)
# counter: pdbs = SpecCounter(mne='pdbs', config_line='6', name='pdbs', unit='0', chan='5', pvname=8idi:scaler1.S6)
# counter: I_APS = SpecCounter(mne='I_APS', config_line='7', name='I_APS', unit='0', chan='6', pvname=8idi:scaler1.S7)
# line 8: CNT008 =     NONE  2  0      1 0x000     ccdc  ccdc
Atten1 = EpicsSignal('8idi:userTran1.P', name='Atten1')
Atten2 = EpicsSignal('8idi:userTran3.P', name='Atten2')
T_A = EpicsSignal('8idi:LS336:TC4:IN1', name='T_A')
T_SET = EpicsSignal('8idi:LS336:TC4:OUT1:SP', name='T_SET')
# counter: APD = SpecCounter(mne='APD', config_line='13', name='APD', unit='0', chan='8', pvname=8idi:scaler1.S9)
