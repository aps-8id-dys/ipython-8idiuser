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
from .qnw_device import *
from .sample_stage import *
from .scaler import *
# from .shutters import *
from .slits import *
from .soft_glue_fpga import *
from .tables import *

# area detectors

# Only do one of these at a time since they create an object with the same name
from .rigaku_500k import *
# from .rigaku_ufxc import *
# from .ad_rigaku_detector import *
# from .ad_rigaku500k import *

# from .lambda_750k import *

# Only do one of these at a time since they create an object with the same name
# from .lambda_2m import *
# from .lambda_2m_QZ import *
# from .eiger500k import *
from .ad_eiger import *
from .ad_lambda2M import *

# non-hardware support
from .data_management import *
