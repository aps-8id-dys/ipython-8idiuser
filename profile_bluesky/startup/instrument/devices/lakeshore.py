
"""
Lakeshore temperature controllers
"""

__all__ = "lakeshore T_A T_SET".split()

from instrument.session_logs import logger
logger.info(__file__)

from apstools.devices import ProcessController
from apstools.synApps.asyn import AsynRecord
from bluesky import plan_stubs as bps
from ophyd import Component, Device, DeviceStatus
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import FormattedComponent
import time


from .epid import pid1, pid2

# TODO: fixes bug in apstools/synApps/asyn.py
class MyAsynRecord(AsynRecord):
    binary_output_maxlength = Component(EpicsSignal, ".OMAX")


class LS336_LoopBase(ProcessController):
    """
    One control loop on the LS336 temperature controller
    
    Each control loop is a separate process controller.
    """
    signal = FormattedComponent(EpicsSignalRO, "{self.prefix}OUT{self.loop_number}:SP_RBV")
    target = FormattedComponent(EpicsSignal, "{self.prefix}OUT{self.loop_number}:SP", kind="omitted")
    units = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}IN{self.loop_number}:Units", kind="omitted")

    loop_name = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}:Name_RBV")
    temperature = FormattedComponent(EpicsSignalRO, "{self.prefix}IN{self.loop_number}")

    control = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Cntrl")
    manual = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:MOUT")
    mode = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OUT{self.loop_number}:Mode")

    def __init__(self, *args, loop_number=None, **kwargs):
        self.controller_name = f"Lakeshore 336 Controller Loop {loop_number}"
        self.loop_number = loop_number
        super().__init__(*args, **kwargs)

    @property
    def settled(self):
        """Is temperature close enough to target?"""
        diff = abs(self.temperature.get() - self.target.get())
        return diff <= self.tolerance.get()

    def get(self, *args, **kwargs):
        return self.signal.get(*args, **kwargs)

    def wait_until_settled(self, timeout=None, timeout_fail=False):
        """
        plan: wait for controller signal to reach target within tolerance
        """
        # see: https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python
        t0 = time.time()
        _st = DeviceStatus(self.signal)

        if self.settled:
            # just in case signal already at target
            _st._finished(success=True)
        else:
            started = False
    
            def changing_cb(*args, **kwargs):
                if started and self.settled:
                    _st._finished(success=True)
    
            token = self.signal.subscribe(changing_cb)
            started = True
            report = 0
            while not _st.done and not self.settled:
                elapsed = time.time() - t0
                if timeout is not None and elapsed > timeout:
                    _st._finished(success=self.settled)
                    msg = f"{self.controller_name} Timeout after {elapsed:.2f}s"
                    msg += f", target {self.target.get():.2f}{self.units.get()}"
                    msg += f", now {self.signal.get():.2f}{self.units.get()}"
                    print(msg)
                    if timeout_fail:
                        raise TimeoutError(msg)
                    continue
                if elapsed >= report:
                    report += self.report_interval_s
                    msg = f"Waiting {elapsed:.1f}s"
                    msg += f" to reach {self.target.get():.2f}{self.units.get()}"
                    msg += f", now {self.temperature.get():.2f}{self.units.get()}"
                    print(msg)
                yield from bps.sleep(self.poll_s)

            self.signal.unsubscribe(token)
            _st._finished(success=self.settled)

        self.record_signal()
        elapsed = time.time() - t0
        print(f"Total time: {elapsed:.3f}s, settled:{_st.success}")


class LS336_LoopMore(LS336_LoopBase):
    """
    Additional controls for loop1 and loop2: heater and pid
    """
    # only on loops 1 & 2
    heater = FormattedComponent(EpicsSignalRO, "{self.prefix}HTR{self.loop_number}")
    heater_range = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}HTR{self.loop_number}:Range")

    pid_P = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}P{self.loop_number}")
    pid_I = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}I{self.loop_number}")
    pid_D = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}D{self.loop_number}")
    ramp_rate = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}RampR{self.loop_number}")
    ramp_on = FormattedComponent(EpicsSignalWithRBV, "{self.prefix}OnRamp{self.loop_number}")


class LS336Device(Device):
    """
    support for Lakeshore 336 temperature controller
    """
    loop1 = FormattedComponent(LS336_LoopMore, "{self.prefix}", loop_number=1)
    loop2 = FormattedComponent(LS336_LoopMore, "{self.prefix}", loop_number=2)
    loop3 = FormattedComponent(LS336_LoopBase, "{self.prefix}", loop_number=3)
    loop4 = FormattedComponent(LS336_LoopBase, "{self.prefix}", loop_number=4)
    
    # same names as apstools.synApps._common.EpicsRecordDeviceCommonAll
    scanning_rate = Component(EpicsSignal, "read.SCAN")
    process_record = Component(EpicsSignal, "read.PROC")
    
    read_all = Component(EpicsSignal, "readAll.PROC")
# TODO: serial = Component(AsynRecord, "serial")
    serial = Component(MyAsynRecord, "serial")
    
    @property
    def value(self):
        """designate one loop as the default signal to return"""
        return self.loop1.signal.get()


lakeshore = LS336Device("8idi:LS336:TC4:", name="lakeshore", labels=["heater", "Lakeshore"])

# shortcuts for generic temperature control
# T_A = lakeshore.loop1.temperature
# T_SET = lakeshore.loop1.target

# QZ changed on 06/23
T_SET = pid1.final_value 
T_A = pid1.controlled_value  
