#!/usr/bin/env python

"""
test issue #114 for FailedStatus exception

see: https://github.com/aps-8id-trr/ipython-8idiuser/issues/114
"""

#from apstools.devices import DeviceMixinBase
from bluesky import RunEngine
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import get_history
from bluesky.utils import ProgressBarManager
import bluesky.plan_stubs as bps
from databroker import Broker
import datetime
import epics
import logging
from ophyd import Component, EpicsSignal
import os
import sys
import time

import ophyd
# logger = logging.getLogger('ophyd.event_dispatcher')
logger = logging.getLogger('ophyd.signal')
logger.setLevel("DEBUG")


if len(sys.argv) == 1:
    CYCLES = 10
elif len(sys.argv) == 2:
    CYCLES = int(sys.argv[1])
DELAY_S = 1e-6
TEST_PV = "8idi:Reg200"

bec = BestEffortCallback()
# db = Broker.named("mongodb_config")
sd = SupplementalData()
pbar_manager = ProgressBarManager()

RE = RunEngine({})
# RE = RunEngine(get_history())
# RE.subscribe(db.insert)
RE.subscribe(bec)
RE.preprocessors.append(sd)
RE.waiting_hook = pbar_manager


pv = EpicsSignal(TEST_PV, name="pv")
pv.wait_for_connection()


def move(signal, label, dest, delay_s):
    yield from bps.checkpoint()
    yield from bps.mv(signal, dest)
    msg = f"{label}:  {dest} {signal.value}"
    # print(msg, os.system("uptime"))
    print(msg, datetime.datetime.now())
    yield from bps.sleep(delay_s)

i = 0
def ping_pong(signal, v1, v2, delay_s=1e-2):
    global i
    yield from move(signal, f"ping {i+1}", v1, delay_s)
    yield from move(signal, f"pong {i+1}", v2, delay_s)
    i += 1


if __name__ == "__main__":
    RE(
        bps.repeater(
            CYCLES,
            ping_pong,
            pv, 
            .1, 
            -.1, 
            delay_s=DELAY_S,
            )
    )

