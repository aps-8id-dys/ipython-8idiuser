logger.info(__file__)

"""detectors (area detectors handled separately)"""

# class LocalScalerCH(ScalerCH):
class LocalScalerCH(DM_DeviceMixinScaler, FixScalerCH):
    
    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the scaler's stage_sigs for acquisition with the DM workflow

        from DM_DeviceMixinScaler
        """
        assert len(args) == 1
        acquire_period = args[0]
        self.stage_sigs["count_mode"] = "AutoCount"
        self.stage_sigs["auto_count_time"] = max(0.1,acquire_period)


_scaler_pv = "8idi:scaler1"
RETRIES = 5
for _retry in range(RETRIES):
    scaler1 = None
    try:
        scaler1 = LocalScalerCH(_scaler_pv, name='scaler1', labels=["scalers", "detectors"])
        break            # success!
    except TimeoutError:
        logger.error(f"attempt #{_retry + 1} failed to connect with PV '{_scaler_pv}'")
        # no need to sleep since each connection attempt has 1 second timeout

if scaler1 is None:
    emsg = f"could not connect with PV '{_scaler_pv}' in {RETRIES} attempts"
    logger.error(emsg)
    raise TimeoutError(emsg)


scaler1.select_channels()   # choose just the channels with EPICS names

timebase = scaler1.channels.chan01.s
pind1 = scaler1.channels.chan02.s
pind2 = scaler1.channels.chan03.s
pind3 = scaler1.channels.chan04.s
pind4 = scaler1.channels.chan05.s
pdbs = scaler1.channels.chan06.s
I_APS = scaler1.channels.chan07.s
I0Mon = scaler1.channels.chan08.s
# APD = scaler1.channels.chan09.s
# cstar_l = scaler1.channels.chan10.s
# cstar_h = scaler1.channels.chan11.s
# oxygen = scaler1.channels.chan12.s

# default_counter will be defined to be pind1,2,3 or 4
default_counter = pind4

for item in (timebase, pind1, pind2, pind3, pind4, pdbs, I_APS, I0Mon):
    item._ophyd_labels_ = set(["channel", "counter",])

Atten1 = EpicsSignalRO('8idi:userTran1.P', name='Atten1', labels=["detectors",])
Atten2 = EpicsSignalRO('8idi:userTran3.P', name='Atten2', labels=["detectors",])
att1 = EpicsSignal('8idi:BioDecode1.A', name='att1', write_pv='8idi:BioEncode1.A')
att2 = EpicsSignal('8idi:BioDecode2.A', name='att2', write_pv='8idi:BioEncode2.A')

# att will be defined to be att1 or att2 based on the ops for the week
att = att2 
