
"""
Soft Glue: FPGA support
"""

__all__ = [
    'soft_glue',
    'sg_control1',
    'pvDELAY_A',
    'pvDELAY_B',
    'sg_num_frames',
]

from instrument.session_logs import logger
logger.info(__file__)

import apstools.devices
from instrument.startup import bps
from ophyd import Component, Device, EpicsSignal



class SoftGlueDevice(Device):

    start_trigger_pulses_sig = Component(EpicsSignal, '8idi:softGlueA:MUX2-1_IN0_Signal')
    reset_trigger_pulses_sig = Component(EpicsSignal, '8idi:softGlueA:OR-1_IN2_Signal')

    # sends  external pulse train signal to the trigger
    # this is a stringout record, value is a str
    send_ext_pulse_tr_sig_to_trig = Component(EpicsSignal, '8idi:softGlueB:BUFFER-1_IN_Signal')

    # sets shutter signal pulse train to single(0)/burst(1) mode
    # this is a stringout record, value is a str
    set_shtr_sig_pulse_tr_mode = Component(EpicsSignal, '8idi:softGlueC:MUX2-1_SEL_Signal')

    # sends detector signal pulse train to burst mode
    # this is a stringout record, value is a str
    send_det_sig_pulse_tr_mode = Component(EpicsSignal, '8idi:softGlueC:MUX2-2_SEL_Signal')

    #this should be 0 or 1 to select the pulse source to be manual or external user device driven respectively
    # this is a stringout record, value is a str
    select_pulse_train_source = Component(EpicsSignal, '8idi:softGlueA:MUX2-1_SEL_Signal')

    acquire_ext_trig_status = Component(EpicsSignal, '8idi:softGlueA:FI2_BI')

    def start_trigger(self):
        # from SPEC macro: Start_SoftGlue_Trigger
        if self.select_pulse_train_source.get() == '0':
            logger.info("Starting detector trigger pulses")
            yield from bps.mv(self.start_trigger_pulses_sig, "1!")
        else:
            logger.info("Waiting for ****User Trigger**** to start acquisition")

    def reset_trigger(self):
        # from SPEC macro: Reset_SoftGlue_Trigger
        logger.info("Resetting detector trigger pulses")
        yield from bps.mv(self.reset_trigger_pulses_sig, "1!")


soft_glue = SoftGlueDevice(name="soft_glue")

# TODO: this could have a better name
sg_control1 = apstools.devices.TransformRecord("8idi:SGControl1", name="sg_control1")

# shortcuts
pvDELAY_A = sg_control1.channels.A.current_value
pvDELAY_B = sg_control1.channels.C.current_value
sg_num_frames = sg_control1.channels.J.current_value
