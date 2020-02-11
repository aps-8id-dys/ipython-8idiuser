"""
local, custom Device definitions
"""

from .aps_source import *
from .pss import *

# upstream devices
from .foe import *
from .monochromator import *
from .be_window import *

# 8-ID-I devices
from .actuators import *
from .attenuators import *
from .crl import *
from .detector_stages import *
from .epid import *
from .fly import *
from .lakeshore import *
from .motors import *
from .preamps import *
from .sample_stage import *
from .scaler import *
from .shutter import *
from .shutter_stage import *
from .slits import *
from .soft_glue import *
from .tables import *

# area detectors
# from .lambda_750k import *    # TODO:
# from .rigaku_qxfc import *    # TODO:

# non-hardware support
from .data_management import *
