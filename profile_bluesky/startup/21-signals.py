logger.info(__file__)

"""signals"""

sys.path.append(os.path.dirname(__file__))
from records.epidRecord import EpidRecord

# APS only:
aps = APS_devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)

undulator = APS_devices.ApsUndulatorDual("ID08", name="undulator")
sd.baseline.append(undulator)


# simulate a shutter (no hardware required)
shutter = SimulatedApsPssShutterWithStatus(name="shutter")
shutter.delay_s = 0.05 # shutter needs short recovery time after moving

pid1 = EpidRecord("8idi:pid1", name="pid1", labels=["pid",])
pid2 = EpidRecord("8idi:pid2", name="pid2", labels=["pid",])
