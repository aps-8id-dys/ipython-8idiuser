logger.info(__file__)

"""gather all the imports here"""


import datetime
from enum import Enum
import getpass 
import itertools
import os
import socket 
import time
import uuid

from ophyd import Component, Device, DeviceStatus, Signal
from ophyd import EpicsMotor, MotorBundle
from ophyd import EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV
from ophyd import FormattedComponent 
from ophyd.scaler import ScalerCH, ScalerChannel
from ophyd.sim import SynSignal

# area detector support (ADSimDetector)
from ophyd import ADBase
from ophyd import ADComponent
from ophyd import AreaDetector
from ophyd import CamBase
from ophyd import FilePlugin
from ophyd import HDF5Plugin, ImagePlugin
from ophyd import SingleTrigger, SimDetector
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import PluginBase
# new in ophyd 1.4.0rc1
from ophyd.areadetector.plugins import GatherPlugin
from ophyd.areadetector.plugins import ScatterPlugin

import apstools.callbacks as APS_callbacks
import apstools.devices as APS_devices
import apstools.filewriters as APS_filewriters
import apstools.plans as APS_plans
import apstools.synApps as APS_synApps
import apstools.suspenders as APS_suspenders
import apstools.utils as APS_utils

# import specific methods by name, we need to customize them sometimes
from apstools.devices import SimulatedApsPssShutterWithStatus
from apstools.filewriters import SpecWriterCallback, spec_comment

# place .ipython/user directory on the path, enables ~"qdo" command:
#    %run -i -m user.module
from IPython.paths import get_ipython_dir
sys.path.append(os.path.join(get_ipython_dir(), "user"))
sys.path.append(os.path.dirname(__file__))
