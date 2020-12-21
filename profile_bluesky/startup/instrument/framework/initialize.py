"""
initialize the bluesky framework
"""

__all__ = [
    "bec",
    "bp",
    "bpp",
    "bps",
    "callback_db",
    "db",
    "np",
    "peaks",
    "RE",
    "sd",
    "summarize_plan",
]

from ..session_logs import logger

logger.info(__file__)

from bluesky import RunEngine
from bluesky import SupplementalData
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.callbacks.broker import verify_files_saved
from bluesky.magics import BlueskyMagics
from bluesky.simulators import summarize_plan
from bluesky.utils import get_history
from bluesky.utils import PersistentDict
from bluesky.utils import ProgressBarManager
from bluesky.utils import ts_msg_hook
from IPython import get_ipython
from ophyd.signal import EpicsSignalBase
import databroker
import os
import sys
import warnings


# convenience imports
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
import numpy as np


# add parent directory of instrument package to import path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",))
)


def get_md_path():
    md_dir_name = "Bluesky_RunEngine_md"
    if os.environ == "win32":
        home = os.environ["LOCALAPPDATA"]
        path = os.path.join(home, md_dir_name)
    else:  # at least on "linux"
        home = os.environ["HOME"]
        path = os.path.join(home, ".config", md_dir_name)
    return path


# check if we need to transition from SQLite-backed historydict
old_md = None
md_path = get_md_path()
if not os.path.exists(md_path):
    logger.info(
        "New directory to store RE.md between sessions: %s", md_path
    )
    os.makedirs(md_path)
    from bluesky.utils import get_history

    old_md = get_history()

# Set up a RunEngine and use metadata backed PersistentDict
RE = RunEngine({})
RE.md = PersistentDict(md_path)
if old_md is not None:
    logger.info("migrating RE.md storage to PersistentDict")
    RE.md.update(old_md)

# keep track of callback subscriptions
callback_db = {}

# Connect with the mongodb database.
db = databroker.catalog["mongodb_config"].v1

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
callback_db["db"] = RE.subscribe(db.insert)

# Set up SupplementalData.
sd = SupplementalData()
RE.preprocessors.append(sd)

# Add a progress bar.
pbar_manager = ProgressBarManager()
RE.waiting_hook = pbar_manager

# Register bluesky IPython magics.
get_ipython().register_magics(BlueskyMagics)

# Set up the BestEffortCallback.
bec = BestEffortCallback()
callback_db["bec"] = RE.subscribe(bec)
peaks = bec.peaks  # just as alias for less typing
bec.disable_baseline()

# uncomment to use these diagnostics

# Verify files saved at end of run, print confirmation message.
# _prv_ = RE.subscribe(post_run(verify_files_saved), 'stop')
# callback_db['post_run_verify'] = _prv_

# Verbose debugging messages.
# ophyd.logger.setLevel(logging.DEBUG)

# RunEngine Message processing
# RE.msg_hook = ts_msg_hook


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=60,
        write_timeout=60,
        connection_timeout=20,
    )
except Exception as exc:
    warnings.warn(
        "ophyd version is old, upgrade to 1.6.0+ "
        "to get set_defaults() method"
    )
    EpicsSignalBase.set_default_timeout(timeout=10, connection_timeout=5)
