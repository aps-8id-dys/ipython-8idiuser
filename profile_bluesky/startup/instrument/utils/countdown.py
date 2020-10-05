
"""
countdown timer
"""


__all__ = """
    countdown_timer
""".split()


from ..session_logs import logger
logger.info(__file__)
import apstools.utils
import time


class CountdownExpired(Exception): ...


@apstools.utils.run_in_thread
def countdown_timer(period_s, permit_signal, msg=None):
    """
    raise :class:`CountdownExpired()` exception if time expires

    PARAMETERS

    period_s
        *float* : time in seconds to expire the timer
    permit_signal
        *obj* : boolean value, instance of `ophyd.Signal`,
        `True` means continue counting down, `False` means end
        the countdown (early)
    msg
        *str* : text reported as reason for exception
        (default: "process to complete")
    """
    msg = msg or "process to complete"
    t0 = time.time()
    time_expired = t0 + period_s

    while permit_signal.get() and time.time() < time_expired:
        time.sleep(0.01)

    if permit_signal.get():
        permit_signal.put(False)
        raise CountdownExpired(
            f"waited {time.time()-t0:.1f}s for {msg}"
        )
