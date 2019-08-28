
"""
Ophyd support for the EPICS calcout record


Public Structures

.. autosummary::
   
    ~calcoutRecord
"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)
from ophyd import EpicsSignal, EpicsSignalRO

from .common_fields import EpicsRecordDeviceCommonAll, EpicsRecordFloatFields
# from .. import utils as APS_utils
from apstools import utils as APS_utils


__all__ = ["calcoutRecord", ]

LIST_CHANNEL_LETTERS = "A B C D E F G H I J K L".split()


class calcoutRecordChannel(Device):
    """channel of a synApps calcout record: A-P"""
    input_value = FC(EpicsSignal,           '{self.prefix}.{self._ch_letter}')
    last_value = FC(EpicsSignalRO,          '{self.prefix}.L{self._ch_letter}')
    input_link = FC(EpicsSignal,            '{self.prefix}.INP{self._ch_letter}')
    input_link_valid = FC(EpicsSignalRO,    '{self.prefix}.IN{self._ch_letter}V')
    
    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)


def _channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (calcoutRecordChannel, '', {'letter': chan})
    return defn


class calcoutRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS calcout record support in ophyd
    
    :see: 
    """
    units = Cpt(EpicsSignal, ".EGU")
    precision = Cpt(EpicsSignal, ".PREC")

    calculated_value = Cpt(EpicsSignal, ".VAL")
    calculation = Cpt(EpicsSignal, ".CALC")

    output_link = Cpt(EpicsSignal, ".OUT")
    output_execute_option = Cpt(EpicsSignal, ".OOPT")
    output_execution_delay = Cpt(EpicsSignal, ".ODLY")
    output_data_option = Cpt(EpicsSignal, ".DOPT")
    output_calculation = Cpt(EpicsSignal, ".OCAL")
    output_value = Cpt(EpicsSignal, ".OVAL")
    invalid_output_action = Cpt(EpicsSignal, ".IVOA")
    invalid_output_value = Cpt(EpicsSignal, ".IVOV")
    event_to_issue = Cpt(EpicsSignal, ".OEVT")

    output_pv_status = Cpt(EpicsSignal, ".OUTV")
    calculation_valid = Cpt(EpicsSignal, ".CLCV")
    output_calculation_valid = Cpt(EpicsSignal, ".OCLV")
    output_delay_active = Cpt(EpicsSignal, ".DLYA")

    hints = {'fields': APS_utils.itemizer("channels.%s", LIST_CHANNEL_LETTERS)}
    read_attrs = APS_utils.itemizer("channels.%s", LIST_CHANNEL_LETTERS)

    channels = DDC(_channels(LIST_CHANNEL_LETTERS))

    @property
    def value(self):
        return self.calculated_value.value
