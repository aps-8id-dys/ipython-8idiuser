logger.info(__file__)

"""signals"""

sys.path.append(os.path.dirname(__file__))
from records.epid import EpidRecord

# APS only:
aps = APS_devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)

undulator = APS_devices.ApsUndulatorDual("ID08", name="undulator")
sd.baseline.append(undulator)


# simulate a shutter (no hardware required)
shutter = SimulatedApsPssShutterWithStatus(name="shutter")
shutter.delay_s = 0.05 # shutter needs short recovery time after moving

class ModifiedEpidRecord(EpidRecord):
    clock_ticks = None

pid1 = ModifiedEpidRecord("8idi:pid1", name="pid1", labels=["pid",])
pid2 = ModifiedEpidRecord("8idi:pid2", name="pid2", labels=["pid",])
