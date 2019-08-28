
"""
Ophyd support for the EPICS transform record


Public Structures

.. autosummary::
   
    ~transformRecord
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

from .common_fields import EpicsRecordDeviceCommonAll
# from .. import utils as APS_utils
from apstools import utils as APS_utils


__all__ = ["transformRecord", ]

LIST_CHANNEL_LETTERS = "A B C D E F G H I J K L M N O P".split()


class transformRecordChannel(Device):
    """channel of a synApps transform record: A-P"""
    current_value = FC(EpicsSignal,         '{self.prefix}.{self._ch_letter}')
    last_value = FC(EpicsSignalRO,          '{self.prefix}.L{self._ch_letter}')
    input_link = FC(EpicsSignal,            '{self.prefix}.INP{self._ch_letter}')
    input_link_valid = FC(EpicsSignalRO,    '{self.prefix}.I{self._ch_letter}V')
    expression_invalid = FC(EpicsSignalRO,  '{self.prefix}.C{self._ch_letter}V')
    comment = FC(EpicsSignal,               '{self.prefix}.CMT{self._ch_letter}')
    expression = FC(EpicsSignal,            '{self.prefix}.CLC{self._ch_letter}')
    output_link = FC(EpicsSignal,           '{self.prefix}.OUT{self._ch_letter}')
    output_link_valid = FC(EpicsSignalRO,   '{self.prefix}.O{self._ch_letter}V')
    
    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)


def _channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (transformRecordChannel, '', {'letter': chan})
    return defn


class transformRecord(EpicsRecordDeviceCommonAll):
    """
    EPICS transform record support in ophyd
    
    :see: https://htmlpreview.github.io/?https://raw.githubusercontent.com/epics-modules/calc/R3-6-1/documentation/transformRecord.html#Fields
    """
    units = Cpt(EpicsSignal, ".EGU")
    precision = Cpt(EpicsSignal, ".PREC")
    version = Cpt(EpicsSignalRO, ".VERS")

    calc_option = Cpt(EpicsSignal, ".COPT")
    invalid_link_action = Cpt(EpicsSignalRO, ".IVLA")
    input_bitmap = Cpt(EpicsSignalRO, ".MAP")

    hints = {'fields': APS_utils.itemizer("channels.%s", LIST_CHANNEL_LETTERS)}
    read_attrs = APS_utils.itemizer("channels.%s", LIST_CHANNEL_LETTERS)

    channels = DDC(_channels(LIST_CHANNEL_LETTERS))
