"""
local, custom Device definitions
"""

from .aps import *
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
from .fly import *
from .lakeshore import *
from .motors import *
from .preamps import *
from .sample_stage import *
from .scaler import *
from .shutter_stage import *
from .slits import *
from .soft_glue import *
from .tables import *

# non-hardware support
from .data_management import *

# TODO:
# from .calcs import *
# from .signals import *
# from .simdet import *
