
"""
EPID: Enhanced Proportional-Integral-Derivative controls
"""

__all__ = ['pid1', 'pid2']

from instrument.session_logs import logger
logger.info(__file__)

from apstools.synApps import EpidRecord
from ophyd import Component, EpicsSignal
from ophyd import Signal


class WaitingEpidRecord(EpidRecord):

    tolerance = Component(Signal, kind="omitted", value=1)  # override in subclass

    @property
    def settled(self):
        """Is following_error within tolerance?"""
        return abs(self.following_error.get()) <= self.tolerance.get()

    def wait_until_settled(self, timeout=None, timeout_fail=False):
        """
        plan: wait for controller signal to reach setpoint within tolerance
        """
        # see: https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python
        t0 = time.time()
        _st = DeviceStatus(self.following_error)

        if self.settled:
            # just in case following_error already within tolerance
            _st._finished(success=True)
        else:
            started = False
    
            def changing_cb(*args, **kwargs):
                if started and self.settled:
                    _st._finished(success=True)
    
            token = self.following_error.subscribe(changing_cb)
            started = True
            report = 0
            while not _st.done and not self.settled:
                elapsed = time.time() - t0
                if timeout is not None and elapsed > timeout:
                    _st._finished(success=self.settled)
                    msg = f"PID loop '{self.name}' Timeout after {elapsed:.2f}s"
                    msg += f", target {self.controlled_value .get():.2f}"
                    msg += f", now {self.final_value.get():.2f}"
                    print(msg)
                    if timeout_fail:
                        raise TimeoutError(msg)
                    continue
                if elapsed >= report:
                    report += self.report_interval_s
                    msg = f"Waiting {elapsed:.1f}s"
                    msg += f" to reach {self.controlled_value.get():.2f}"
                    msg += f", now {self.final_value.get():.2f}"
                    print(msg)
                yield from bps.sleep(self.poll_s)

            self.following_error.unsubscribe(token)
            _st._finished(success=self.settled)

        self.record_signal()
        elapsed = time.time() - t0
        print(f"Total time: {elapsed:.3f}s, settled:{_st.success}")


pid1 = WaitingEpidRecord("8idi:pid1", name="pid1", labels=["pid",])
pid2 = WaitingEpidRecord("8idi:pid2", name="pid2", labels=["pid",])
