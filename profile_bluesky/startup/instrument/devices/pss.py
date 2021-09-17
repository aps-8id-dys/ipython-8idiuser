
"""
APS Personnel Safety System
"""

__all__ = [
    'pss',
    'operations_in_8idi',
]

from instrument.session_logs import logger
logger.info(__file__)

import apstools.suspenders 
from ..framework import RE
from ..devices import aps
from ophyd import Component, Device, EpicsSignalRO


class PSS_Parameters(Device):
    a_beam_active = Component(EpicsSignalRO, "PA:08ID:A_BEAM_ACTIVE.VAL", string=True, labels=["pss",])

    d_shutter_open_chain_A = Component(EpicsSignalRO, "PA:08ID:STA_D_SDS_OPEN_PL.VAL", string=True, labels=["pss",])
    d_shutter_closed_chain_B = Component(EpicsSignalRO, "PB:08ID:STA_D_SDS_CLSD_PL", string=True, labels=["pss",])

    i_shutter_open_chain_A = Component(EpicsSignalRO, "PA:08ID:STA_F_SFS_OPEN_PL", string=True, labels=["pss",])
    i_shutter_closed_chain_B = Component(EpicsSignalRO, "PB:08ID:STA_F_SFS_CLSD_PL", string=True, labels=["pss",])
    i_station_searched_chain_A = Component(EpicsSignalRO, "PA:08ID:STA_F_SEARCHED_PL.VAL", string=True, labels=["pss",])

    @property
    def i_station_enabled(self):
        """
        look at the switches: are we allowed to operate?
    
        # Station I has a shutter to control beam entering
        # but the user may open or close that shutter at will.
        # The upstream D shutter (at exit of A station) defines 
        # whether the I station can operate,
        # so that's the component we need to make a determination
        # whether or not the I station is enabled.
        
        # I station operations are enabled if D shutter is OPEN
        """
        enabled = self.d_shutter_open_chain_A.get() == "ON"
        return enabled


def operations_in_8idi():
    """
    returns True if allowed to use X-ray beam in 8-ID-I station
    """
    return pss.i_station_enabled


pss = PSS_Parameters(name="pss")

# bluesky session should restart if this changes
msg = "D station shutter changed.  This affects whether or not"
msg += " I station can take beam and whether simulators are"
msg += " used.  Resume is not allowed from this condition."
msg += " You are strongly advised to exit and restart"
msg += " the bluesky session."

if aps.inUserOperations and operations_in_8idi():
    suspend_I_station_status = apstools.suspenders.SuspendWhenChanged(
        pss.d_shutter_open_chain_A, 
        # expected_value=1,
        # QZ changed to "ON" on 09/14/2021
        expected_value="ON", 
        tripped_message=msg)
    RE.install_suspender(suspend_I_station_status)
else:
    logger.warning("not is user operations, no suspender installed for D-station shutter")
