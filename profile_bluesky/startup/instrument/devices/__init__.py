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
from .shutters import *
from .slits import *
from .soft_glue_fpga import *
from .tables import *

# area detectors
from .lambda_750k import *
# from .lambda_2m import *
from .rigaku_ufxc import *

# non-hardware support
from .data_management import *
