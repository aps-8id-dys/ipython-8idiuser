
# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)

import subprocess 
import datetime


class UFXC_Device(Device):
    shutter_control = Component(EpicsSignal, "8idi:softGlueC:AND-4_IN2_Signal")
    acquire_start = Component(EpicsSignal, "8idi:Unidig2Bo7.VAL")
    acquire_complete = Component(EpicsSignal, "8idi:Unidig2Bi2.VAL")

UFXC = UFXC_Device(name = "UFXC")


def UFXC_Acquire(batch_name='A001_Test'):

    # TODO: refactor like user.Lambda.AD_Acquire

    yield from bps.mv(UFXC.shutter_control, 'UFXC')
    cmd = f"echo FILE:F:{batch_name} | nc 164.54.116.83 10000"
    exitcode = APS_utils.unix(cmd)    # FIXME: blocking code!!!
    # If exitcode not equal b'', then an error has occurred
    print(f"START of UFXC Measurement: {datetime.datetime.now()}")

    yield from bps.mv(UFXC.acquire_start, 1)
    yield from bps.sleep(0.1)
    yield from bps.mv(UFXC.acquire_start, 0)
       
    yield from bps.sleep(0.2)

    print("Waiting for UFXC to finish DAQ and ready for next Daq")

    while UFXC.acquire_complete.get() not in (1, 'High'):
        yield from bps.sleep(0.01)  # FIXME: use a status object instead
    print(f"UFXC is ready to start the next DAQ: {UFXC.acquire_complete.value}")

    print(f"END of UFXC Measurement: {datetime.datetime.now()}")
