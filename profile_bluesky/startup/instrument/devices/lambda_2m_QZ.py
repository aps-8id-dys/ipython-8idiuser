
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt

# merged class
class Lambda2M_Cam1(Device):
    """CAM1"""

    acquire = Cpt(EpicsSignal, "Acquire", put_complete=False)
    detector_state = Cpt(EpicsSignal, "DetectorState_RBV")


class Lambda2M_HDF1(Device):
    """HDF1"""

    capture = Cpt(EpicsSignal, "Capture")
    capture_rbv = Cpt(EpicsSignal, "Capture_RBV")


class Lambda2M(Device):
    """Detector object"""

    cam1 = Cpt(Lambda2M_Cam1, "cam1:", name="cam1")
    hdf1 = Cpt(Lambda2M_HDF1, "HDF1:", name="hdf1")


# Create the detector object
lambda2m = Lambda2M(
    "8idLambda2m:", name="lambda2m", labels=["lambda2m", "areadetectors", "detectors"]
)
