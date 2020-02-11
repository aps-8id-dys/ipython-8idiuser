
"""
fly stage
"""

__all__ = [
    'flyz',
    'flyscan',
]

from instrument.session_logs import logger
logger.info(__file__)

from instrument.startup import bps
from ophyd import Component, Device, EpicsMotor, EpicsSignal, Signal
from ophyd import DeviceStatus
import threading


class PSO_TaxiFly_Device(Device):
    """
    Operate the motion trajectory controls of an Aerotech Ensemble controller
    
    note: PSO means Position Synchronized Output (Aerotech's term)
    
    USAGE:
    
        # create an object
        pso1 = PSO_TaxiFly_Device("2bmb:PSOFly1:", name="pso1")
        
        # in a plan, use this
        yield from abs_set(pso1, "taxi", wait=True)
        yield from abs_set(pso1, "fly", wait=True)
    """
    slew_speed = Component(EpicsSignal, "slewSpeed.VAL")
    scan_control = Component(EpicsSignal, "scanControl.VAL", string=True)
    start_pos = Component(EpicsSignal, "startPos.VAL")
    end_pos = Component(EpicsSignal, "endPos.VAL")
    scan_delta = Component(EpicsSignal, "scanDelta.VAL")
    pso_taxi = Component(EpicsSignal, "taxi.VAL", put_complete=True)
    pso_fly = Component(EpicsSignal, "fly.VAL", put_complete=True)
    busy = Signal(value=False, name="busy")

    enabled = True  # True or False  (was `FLY_SCAN_YES_NO` in SPEC)
    
    def setup(self, start_pos, end_pos, slew_speed):
        """
        convenience plan: define the fly scan range parameters
        """
        yield from bps.mv(
            self.start_pos, start_pos,
            self.end_pos, end_pos,
            self.slew_speed, slew_speed,
        )
    
    def taxi(self):
        """
        request move to taxi position, interactive use

        Note: This method is NOT a bluesky plan.
        
        Since ``pso_taxi`` has the ``put_complete=True`` attribute,
        this will block until the move is complete.
        
        (note: ``2bmb:PSOFly1:taxi.RTYP`` is a ``busy`` record.)
        """
        logger.debug("starting TAXI to position")
        self.pso_taxi.put("Taxi")
    
    def fly(self):
        """
        request fly scan to start, interactive use

        Note: This method is NOT a bluesky plan.
        
        Since ``pso_fly`` has the ``put_complete=True`` attribute,
        this will block until the move is complete.
        """
        logger.debug("starting FLY")
        self.pso_fly.put("Fly")

    def set(self, value):       # interface for BlueSky plans
        """value is either Taxi or Fly"""
        # """value is either Taxi, Fly, or Return"""
        allowed = "Taxi Fly".split()
        if str(value).lower() not in list(map(str.lower, allowed)):
            msg = "value should be one of: " + " | ".join(allowed)
            msg + " received " + str(value)
            raise ValueError(msg)

        if self.busy.get():
            raise RuntimeError("PSO device is operating")

        status = DeviceStatus(self)
        
        def action():
            """the real action of ``set()`` is here"""
            if str(value).lower() == "taxi":
                self.taxi()
            elif str(value).lower() == "fly":
                self.fly()
            # elif str(value).lower() == "return":
            #     self.motor.move(self.return_position)

        def run_and_wait():
            """handle the ``action()`` in a thread"""
            self.busy.put(True)
            action()
            self.busy.put(False)
            status._finished(success=True)
        
        threading.Thread(target=run_and_wait, daemon=True).start()
        return status


flyz = EpicsMotor('8idiAERO:aero:c0:m1', name='flyz', labels=("motor",))
flyscan = PSO_TaxiFly_Device("8idiAERO:PSOFly1:", name="flyscan")
