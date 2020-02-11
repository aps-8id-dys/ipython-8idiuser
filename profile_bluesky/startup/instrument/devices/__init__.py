"""
local, custom Device definitions

DEVICES

*    BeamSplittingMonochromatorDevice()
*    BeWindow()
*    CompoundRefractiveLensDevice()
*    DetStageDownstream()
*    DetStageUpstream()
*    FlightPathTable()
*    FOEmirrorDevice()
*    FOEpinholeDevice()
*    LS336Device()
*    MonochromatorDevice()
*    MonochromatorTableDevice()
*    PreampDevice()
*    PreampUnitNumberDevice()
*    PSO_TaxiFly_Device()
*    PSS_Parameters()
*    #SamplePiezo()
*    SampleStage()
*    SampleStageTable()
*    ShutterStage()
*    SlitI1Device()
*    SlitI2Device()
*    SlitI3Device()
*    SlitI4Device()
*    SlitI5Device()
*    SlitIpinkDevice()
*    SoftGlueDevice()
*    TableOptics()
*    WBslitDevice()
"""

from .aps import *
from .pss import *

# upstream devices
from .foe import *
from .monochromator import *
from .be_window import *

# 8-ID-I devices
from .actuators import *
from .crl import *
from .detector_stages import *
from .fly import *
from .lakeshore import *
from .motors import *
from .preamps import *
from .sample_stage import *
from .shutter_stage import *
from .slits import *
from .soft_glue import *
from .tables import *

# non-hardware support
from .data_management import *

# TODO:
# from .calcs import *
# from .scaler import *
# from .signals import *
# from .simdet import *
