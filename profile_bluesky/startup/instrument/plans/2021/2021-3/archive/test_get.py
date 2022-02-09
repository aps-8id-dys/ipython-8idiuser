
from instrument.framework import bec, RE
from instrument.devices import lakeshore, flyscan, adrigaku
from instrument.plans import AD_Acquire, movesample, select_RIGAKU
from bluesky import plans as bp
from bluesky import plan_stubs as bps
from instrument.collection import *
from instrument.devices import aps


def test():
    if rigaku500k.cam.acquire.get() == 0:
        yield from bps.mv(rigaku500k.cam.acquire_time, 0.1)


    


