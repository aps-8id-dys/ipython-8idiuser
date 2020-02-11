
"""
preamplifiers
"""

__all__ = ['preamps',]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsSignalRO


class PreampUnitNumberDevice(Device):
    units = Component(EpicsSignalRO, 'sens_unit', string=True)
    number = Component(EpicsSignalRO, 'sens_num')
    
    unit_gains = {
		"mA/V": 1e-3,
		"uA/V": 1e-6,
		"nA/V": 1e-9,
		"pA/V": 1e-12,
	}

    @property
    def amp_scale(self):
        enums = self.number.enum_strs
        sensitivity_index = self.number.get()
        sensitivity = float(enums[sensitivity_index])

        units = self.units.get()
        gain = self.unit_gains[units]

        return gain * sensitivity


class PreampDevice(Device):
    pind1 = Component(PreampUnitNumberDevice, '8idi:A1')
    pind2 = Component(PreampUnitNumberDevice, '8idi:A2')
    pind3 = Component(PreampUnitNumberDevice, '8idi:A3')
    pind4 = Component(PreampUnitNumberDevice, '8idi:A4')
    pdbs = Component(PreampUnitNumberDevice, '8idi:A5')

    @property
    def gains(self):
        """
        return dictionary of Amps/V (gains) for all preamplifiers
        """
        Amps_per_Volt = {}
        for nm in self.component_names:
            amp = self.__getattribute__(nm)
            Amps_per_Volt[nm] = amp.amp_scale
        return Amps_per_Volt


preamps = PreampDevice(name="preamps")
