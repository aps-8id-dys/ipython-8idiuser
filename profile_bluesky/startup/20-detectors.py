logger.info(__file__)

"""detectors (area detectors handled separately)"""

class LocalScalerCH(ScalerCH):
    
    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the scaler's stage_sigs for acquisition with the DM workflow

        Implement this method in _any_ Device that requires custom
        setup for the DM workflow.
        """
        assert len(args) == 1
        acquire_period = args[0]
        self.stage_sigs["count_mode"] = "AutoCount"
        self.stage_sigs["auto_count_time"] = max(0.1,acquire_period)


scaler1 = LocalScalerCH('8idi:scaler1', name='scaler1', labels=["scalers", "detectors"])

_timeout = time.time() + 10
while time.time() < _timeout:
    if scaler1.connected:
        break
    time.sleep(0.2)
if time.time() > _timeout:
    msg = "10s timeout expired waiting for scaler1 to connect"
    raise RuntimeError(msg)
del _timeout

scaler1.select_channels(None)   # choose just the channels with EPICS names

timebase = scaler1.channels.chan01.s
pind1 = scaler1.channels.chan02.s
pind2 = scaler1.channels.chan03.s
pind3 = scaler1.channels.chan04.s
pind4 = scaler1.channels.chan05.s
pdbs = scaler1.channels.chan06.s
I_APS = scaler1.channels.chan07.s
I0Mon = scaler1.channels.chan08.s
# APD = scaler1.channels.chan09.s
for o in (timebase, pind1, pind2, pind3, pind4, pdbs, I_APS, I0Mon):
    o._ophyd_labels_ = set(["counter",] + list(o._ophyd_labels_))

Atten1 = EpicsSignalRO('8idi:userTran1.P', name='Atten1', labels=["detectors",])
Atten2 = EpicsSignalRO('8idi:userTran3.P', name='Atten2', labels=["detectors",])
att1 = EpicsSignal('8idi:BioDecode1.A', name='att1', write_pv='8idi:BioEncode1.A')
att2 = EpicsSignal('8idi:BioDecode2.A', name='att2', write_pv='8idi:BioEncode2.A')
