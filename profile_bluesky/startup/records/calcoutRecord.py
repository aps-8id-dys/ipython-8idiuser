
"""
Ophyd support for the EPICS calcout record


Public Structures

.. autosummary::
   
    ~userCalcoutDevice
    ~calcoutRecord
    ~calcoutRecordChannel
    ~calcout_setup_gaussian
    ~calcout_setup_lorentzian
    ~calcout_setup_incrementer
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
from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor

from .common_fields import EpicsRecordDeviceCommonAll, EpicsRecordFloatFields
# from .. import utils as APS_utils
from apstools import utils as APS_utils


__all__ = [
	"userCalcoutDevice",
	"calcoutRecord",
	"calcoutRecordChannel",
    "calcout_setup_gaussian",
    "calcout_setup_lorentzian",
    "calcout_setup_incrementer",
	]

LIST_CHANNEL_LETTERS = "A B C D E F G H I J K L".split()


class calcoutRecordChannel(Device):
    """
    channel of a synApps calcout record: A-L

	.. autosummary::
	   
		~reset
    """
    input_value = FC(EpicsSignal,       '{self.prefix}.{self._ch_letter}')
    last_value = FC(EpicsSignalRO,      '{self.prefix}.L{self._ch_letter}')
    input_pv = FC(EpicsSignal,          '{self.prefix}.INP{self._ch_letter}')
    input_pv_valid = FC(EpicsSignalRO,  '{self.prefix}.IN{self._ch_letter}V')
    
    read_attrs = ['input_value',]
    hints = {"fields": read_attrs}

    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_value.put(0)
        self.input_pv.put("")


def _channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (calcoutRecordChannel, '', {'letter': chan})
    return defn


class calcoutRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS calcout record support in ophyd

	.. autosummary::
	   
		~reset
    """
    units = Cpt(EpicsSignal, ".EGU")
    precision = Cpt(EpicsSignal, ".PREC")

    calculated_value = Cpt(EpicsSignal, ".VAL")
    calculation = Cpt(EpicsSignal, ".CALC")

    output_pv = Cpt(EpicsSignal, ".OUT")
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

    channels = DDC(_channels(LIST_CHANNEL_LETTERS))

    read_attrs = APS_utils.itemizer("channels.%s", LIST_CHANNEL_LETTERS)
    hints = {'fields': read_attrs}

    @property
    def value(self):
        return self.calculated_value.value
    
    def reset(self):
        """set all fields to default values"""
        pvname = self.description.pvname.split(".")[0]
        self.scanning_rate.put("Passive")
        self.description.put(pvname)
        self.units.put("")
        self.precision.put("5")

        self.calculation.put("")
        self.calculated_value.put(0)
        self.output_calculation.put("")
        self.output_value.put(0)

        self.forward_link.put("")
        self.output_pv.put("")
        self.invalid_output_action.put(0)
        self.invalid_output_value.put(0)

        self.output_execution_delay.put(0)
        self.output_execute_option.put(0)
        self.output_data_option.put(0)

        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(channel, calcoutRecordChannel):
                channel.reset()
        self.hints = {'fields': ["channels.%s" % c for c in LIST_CHANNEL_LETTERS]}
        self.read_attrs = ["channels.%s" % c for c in LIST_CHANNEL_LETTERS]


class userCalcoutDevice(Device):
    """
    synApps XXX IOC setup of user calcouts: $(P):userCalcOut$(N)

    .. autosummary::
       
        ~reset

    """

    enable = Cpt(EpicsSignal, 'userCalcOutEnable')
    calcout1 = Cpt(calcoutRecord, 'userCalcOut1')
    calcout2 = Cpt(calcoutRecord, 'userCalcOut2')
    calcout3 = Cpt(calcoutRecord, 'userCalcOut3')
    calcout4 = Cpt(calcoutRecord, 'userCalcOut4')
    calcout5 = Cpt(calcoutRecord, 'userCalcOut5')
    calcout6 = Cpt(calcoutRecord, 'userCalcOut6')
    calcout7 = Cpt(calcoutRecord, 'userCalcOut7')
    calcout8 = Cpt(calcoutRecord, 'userCalcOut8')
    calcout9 = Cpt(calcoutRecord, 'userCalcOut9')
    calcout10 = Cpt(calcoutRecord, 'userCalcOut10')

    def reset(self):
        """set all fields to default values"""
        self.calcout1.reset()
        self.calcout2.reset()
        self.calcout3.reset()
        self.calcout4.reset()
        self.calcout5.reset()
        self.calcout6.reset()
        self.calcout7.reset()
        self.calcout8.reset()
        self.calcout9.reset()
        self.calcout10.reset()
        self.read_attrs = ["calcout%d" % (c+1) for c in range(10)]
        self.read_attrs.insert(0, "enable")


def _setup_peak_calcout_(calc, desc, calcout, motor, center=0, width=1, scale=1, noise=0.05):
    """internal: setup that is common to both Gaussian and Lorentzian calcout"""
    # to add a noisy background will need another calc
    assert(isinstance(motor, EpicsMotor))
    assert(isinstance(calcout, calcoutRecord))
    assert(width > 0)
    assert(0.0 <= noise <= 1.0)
    calcout.reset()
    calcout.scanning_rate.put("Passive")
    calcout.channels.A.input_pv.put(motor.user_readback.pvname)
    calcout.channels.B.input_value.put(center)
    calcout.channels.C.input_value.put(width)
    calcout.channels.D.input_value.put(scale)
    calcout.channels.E.input_value.put(noise)
    calcout.calculation.put(calc)
    calcout.scanning_rate.put(".1 second")
    calcout.description.put(desc)

    calcout.read_attrs = ['input_value',]
    calcout.hints = {"fields": calcout.read_attrs}


def calcout_setup_gaussian(calcout, motor, center=0, width=1, scale=1, noise=0.05):
    """setup calcout for noisy Gaussian"""
    _setup_peak_calcout_(
        "D*(0.95+E*RNDM)/exp(((A-b)/c)^2)",
        "noisy Gaussian curve", 
        calcout, 
        motor, 
        center=center, 
        width=width, 
        scale=scale, 
        noise=noise)


def calcout_setup_lorentzian(calcout, motor, center=0, width=1, scale=1, noise=0.05):
    """setup calcout record for noisy Lorentzian"""
    _setup_peak_calcout_(
        "D*(0.95+E*RNDM)/(1+((A-b)/c)^2)", 
        "noisy Lorentzian curve", 
        calcout, 
        motor, 
        center=center, 
        width=width, 
        scale=scale, 
        noise=noise)


def calcout_setup_incrementer(calcout, scan=None, limit=100000):
    """setup calcout record as an incrementer"""
    # consider a noisy background, as well (needs a couple calcs)
    scan = scan or ".1 second"
    calcout.reset()
    calcout.scanning_rate.put("Passive")
    calcout.description.put("incrementer")
    pvname = calcout.calculated_value.pvname.split(".")[0]
    calcout.channels.A.input_pv.put(pvname)
    calcout.channels.B.input_value.put(limit)
    calcout.calculation.put("(A+1) % B")
    calcout.scanning_rate.put(scan)

    calcout.hints = {"fields": ['input_value',]}
    calcout.read_attrs = ['input_value',]
