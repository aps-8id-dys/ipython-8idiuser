"""
Ophyd detector class customized for Eigker500k from Eiger.

"""

from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt

# from bluesky import plan_stubs as bps

# softglue_trigger =  ophyd.EpicsSignal("8idi:softGlueA:MUX2-1_IN0_Signal", name="softglue_trigger")

# merged class
class Eiger500k_Cam1(Device):
    """CAM1"""
    cam_acquire = Cpt(EpicsSignal, "Acquire") 
    cam_acquire_busy = Cpt(EpicsSignal, "AcquireBusy")
    cam_bad_frame_counter = Cpt(EpicsSignal, "BadFrameCounter_RBV")
    cam_num_images = Cpt(EpicsSignal, "NumImages")
    
class Eiger500k_HDF1(Device):
    """HDF1"""
    hdf_capture = Cpt(EpicsSignal, "Capture")

class Eiger500k(Device):
    """Detector object"""
    cam1 = Cpt(Eiger500k_Cam1, "cam1:")
    hdf1 = Cpt(Eiger500k_HDF1, "HDF1:")


# Create the detector object
eiger500k = Eiger500k(
    "dp_eiger_xrd4:", name="eiger500k", labels=["eiger500k", "areadetectors", "detectors"]
)
