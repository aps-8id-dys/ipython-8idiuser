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

crl = CompoundRefractiveLensDevice(name="crl")
monochromator = MonochromatorDevice(name="monochromator")
WBslit = WBslitDevice(name="WBslit")
si1 = SlitI1Device(name="si1")
si2 = SlitI2Device(name="si2")
si3 = SlitI3Device(name="si3")
si4 = SlitI4Device(name="si4")
si5 = SlitI5Device(name="si5")
sipink = SlitIpinkDevice(name="sipink")
foepinhole = FOEpinholeDevice(name="foepinhole")
foemirror = FOEmirrorDevice(name="foemirror")
diamond = BeamSplittingMonochromatorDevice(name="diamond")
opticstable = TableOptics(name="opticstable")
flightpathtable = FlightPathTable(name="flightpathtable")
bewindow = BeWindow(name="bewindow")
shutterstage = ShutterStage(name="shutterstage")
detu = DetStageUpstream(name="detu")
detd = DetStageDownstream(name="detd")
samplestage = SampleStage(name="samplestage")

class ModifiedEpidRecord(EpidRecord):
    clock_ticks = None

pid1 = ModifiedEpidRecord("8idi:pid1", name="pid1", labels=["pid",])
pid2 = ModifiedEpidRecord("8idi:pid2", name="pid2", labels=["pid",])
