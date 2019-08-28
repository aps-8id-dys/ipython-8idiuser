
"""
Ophyd support for the EPICS epid record


Public Structures

.. autosummary::
   
    ~epidRecord

:see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
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

from ophyd.device import Device, Component
from ophyd import EpicsSignal, EpicsSignalRO


__all__ = ["epidRecord", ]


class epidRecord(Device):
    proportional_gain = Component(EpicsSignal, ".KP")
    integral_gain = Component(EpicsSignal, ".KI")
    derivative_gain = Component(EpicsSignal, ".KD")
    following_errror = Component(EpicsSignalRO, ".ERR")
    calculated_P = Component(EpicsSignalRO, ".P")
    calculated_I = Component(EpicsSignal, ".I")
    calculated_D = Component(EpicsSignalRO, ".D")
    output_value = Component(EpicsSignalRO, ".OVAL")
    clock_ticks = Component(EpicsSignalRO, ".CT")
    time_difference = Component(EpicsSignal, ".DT")
    high_limit = Component(EpicsSignal, ".DRVH")
    low_limit = Component(EpicsSignal, ".DRVL")
    
    # TODO: additional fields common to all records (such as alarms)
    description = Component(EpicsSignal, ".DESC")

    # TODO: additional fields common to similar records (such as operating range)
    units = Component(EpicsSignal, ".EGU")
    precision = Component(EpicsSignal, ".PREC")
    
    @property
    def value(self):
        return self.output_value.value
