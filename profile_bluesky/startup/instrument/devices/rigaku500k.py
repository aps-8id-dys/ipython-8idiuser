"""
Ophyd detector class customized for Rigaku.

Use this instead of CamBase to tackle unpredictable PV behaviors from Rigaku R&D detector
"""


from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt

# from bluesky import plan_stubs as bps


# merged class
class Rigaku500k_Cam1(Device):
    """CAM1"""

    acquire_time = Cpt(EpicsSignal, "AcquireTime")
    image_mode = Cpt(EpicsSignal, "ImageMode")
    trigger_mode = Cpt(EpicsSignal, "TriggerMode")
    num_images = Cpt(EpicsSignal, "NumImages")
    corrections = Cpt(EpicsSignal, "Corrections")
    data_type = Cpt(EpicsSignal, "DataType")
    det_state = Cpt(EpicsSignal, "DetectorState_RBV", string=True)
    file_name = Cpt(EpicsSignal, "FileName", string=True)
    file_path = Cpt(EpicsSignal, "FilePath", string=True)
    acquire = Cpt(EpicsSignal, "Acquire", put_complete=False)
    num_que_arrays = Cpt(EpicsSignal, "NumQueuedArrays")


class Rigaku500k_HDF1(Device):
    """HDF1"""

    auto_inc = Cpt(EpicsSignal, "AutoIncrement")
    num_capture = Cpt(EpicsSignal, "NumCapture")
    file_name = Cpt(EpicsSignal, "FileName", string=True)
    file_num = Cpt(EpicsSignal, "FileNumber")
    capture = Cpt(EpicsSignal, "Capture_RBV")


class Rigaku500k(Device):
    """Detector object"""

    cam1 = Cpt(Rigaku500k_Cam1, "cam1:", name="cam1")
    hdf1 = Cpt(Rigaku500k_HDF1, "HDF1:", name="hdf1")


# Create the detector object
rigaku500k = Rigaku500k(
    "8idRigaku:", name="rigaku500k", labels=["rigaku", "areadetectors", "detectors"]
)
