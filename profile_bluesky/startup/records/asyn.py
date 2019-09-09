
"""
Ophyd support for the EPICS asyn record


Public Structures

.. autosummary::
   
    ~AsynRecord

:see: https://github.com/epics-modules/asyn
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

from ophyd.device import Component
from ophyd import EpicsSignal, EpicsSignalRO
from apstools.synApps._common import EpicsRecordDeviceCommonAll
from apstools.synApps._common import EpicsRecordFloatFields


__all__ = ["AsynRecord", ]


class AsynRecord(EpicsRecordDeviceCommonAll):
    """
    EPICS asyn record support in ophyd
    
    :see: https://epics.anl.gov/modules/soft/asyn/R4-36/asynRecord.html
    :see: https://github.com/epics-modules/asyn
    :see: https://epics.anl.gov/modules/soft/asyn/
    """
    ascii_output = Component(EpicsSignal, ".AOUT")
    # .BMAX  binary_output_maxlength
    # .BOUT  binary_output
    # .EOMR  end_of_message_reason
    input_format = Component(EpicsSignalRO, ".IFMT")
    interface = Component(EpicsSignal, ".IFACE")
    number_bytes_actually_read = Component(EpicsSignalRO, ".NRRD")
    number_bytes_actually_written = Component(EpicsSignalRO, ".NAWT")
    number_bytes_to_read = Component(EpicsSignal, ".NORD")
    number_bytes_to_write = Component(EpicsSignal, ".NOWT")
    octet_is_valid = Component(EpicsSignalRO, ".OCTETIV")
    output_format = Component(EpicsSignalRO, ".OFMT")
    terminator_input = Component(EpicsSignal, ".IEOS")
    terminator_output = Component(EpicsSignal, ".OEOS")
    timeout = Component(EpicsSignal, ".TMOT")
    transaction_mode = Component(EpicsSignal, ".TMOD")
    translated_input = Component(EpicsSignal, ".TINP")
