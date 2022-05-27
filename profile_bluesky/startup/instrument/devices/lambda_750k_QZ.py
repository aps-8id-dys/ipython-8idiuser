
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt

# merged class
class Lambda750k_Cam1(Device):
    """CAM1"""

    acquire = Cpt(EpicsSignal, "Acquire", put_complete=False)
    detector_state = Cpt(EpicsSignal, "DetectorState_RBV")


class Lambda750k_HDF1(Device):
    """HDF1"""

    capture = Cpt(EpicsSignal, "Capture")
    capture_rbv = Cpt(EpicsSignal, "Capture_RBV")


class Lambda750k(Device):
    """Detector object"""

    cam1 = Cpt(Lambda750k_Cam1, "cam1:", name="cam1")
    hdf1 = Cpt(Lambda750k_HDF1, "HDF1:", name="hdf1")


# Create the detector object
Lambda750k = Lambda750k(
    "8idLambda750k:", name="lambda750k", labels=["lambda750k", "areadetectors", "detectors"]
)
