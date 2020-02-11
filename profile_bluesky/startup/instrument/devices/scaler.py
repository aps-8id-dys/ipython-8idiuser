
"""
scaler support (area detectors handled separately)
"""

__all__ = """
    scaler1
    timebase
    pind1
    pind2
    pind3
    pind4
    pdbs
    I_APS
    I0Mon
    default_counter
    """.split()

from ..session_logs import logger
logger.info(__file__)

from .data_management import DM_DeviceMixinScaler
from ophyd.scaler import ScalerCH
from ophyd import Kind


def safeOphydName(text):
    """
    make text safe to be used as an ophyd object name

    Given some input text string, return a clean version.
    Remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.
    """
    import re
    pattern = "[a-zA-Z0-9_]"

    def mapper(c):
        if re.match(pattern, c) is not None:
            return c
        return "_"

    return "".join([mapper(c) for c in text])




class FixScalerCH(ScalerCH):

    def select_channels(self, chan_names=[]):
        '''Select channels based on the EPICS name PV

        Parameters
        ----------
        chan_names : Iterable[str] or None

            The names (as reported by the channel.chname signal)
            of the channels to select.
            If *None*, select all channels named in the EPICS scaler.
        '''
        self.match_names()  # name channels by EPICS names
        name_map = {}
        for i, s in enumerate(self.channels.component_names):
            channel = getattr(self.channels, s)
            # just in case the name is not yet safe
            channel.s.name = safeOphydName(channel.s.name)
            nm = channel.s.name  # as defined in scaler.match_names()
            if i == 0 and len(nm) == 0:
                nm = "clock"        # ALWAYS get the clock channel
            if len(nm) > 0:
                name_map[nm] = s

        # previous argument was chan_names=None to select all
        # include logic here that allows backwards-compatibility
        if len(chan_names or []) == 0:    # default setting
            chan_names = name_map.keys()

        read_attrs = []
        for ch in chan_names:
            try:
                read_attrs.append(name_map[ch])
            except KeyError:
                raise RuntimeError("The channel {} is not configured "
                                    "on the scaler.  The named channels are "
                                    "{}".format(ch, tuple(name_map)))

        self.channels.kind = Kind.normal
        self.channels.read_attrs = list(read_attrs)
        self.channels.configuration_attrs = list(read_attrs)

        for i, s in enumerate(self.channels.component_names):
            channel = getattr(self.channels, s)
            if s in read_attrs:
                channel.s.kind = Kind.hinted
            else:
                channel.s.kind = Kind.normal


class LocalScalerCH(DM_DeviceMixinScaler, FixScalerCH):
    
    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the scaler's stage_sigs for acquisition with the DM workflow
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
