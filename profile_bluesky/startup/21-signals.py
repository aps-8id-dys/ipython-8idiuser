logger.info(__file__)

"""signals"""

# APS only:
aps = APS_devices.ApsMachineParametersDevice(name="aps")
sd.baseline.append(aps)

undulator = APS_devices.ApsUndulatorDual("ID08", name="undulator")
sd.baseline.append(undulator)

pss = PSS_Parameters(name="pss")
# bluesky session should restart if this changes
msg = "D station shutter changed.  This affects whether or not"
msg += " I station can take beam and whether simulators are"
msg += " used.  Resume is not allowed from this condition."
msg += " You are strongly advised to exit and restart"
msg += " the bluesky session."
suspend_I_station_status = APS_suspenders.SuspendWhenChanged(
    pss.d_shutter_open_chain_A, 
    expected_value=1,
    tripped_message=msg)
RE.install_suspender(suspend_I_station_status)


def operations_in_8idi():
    """
    returns True if allowed to use X-ray beam in 8-ID-I station
    """
    return pss.i_station_enabled


if aps.inUserOperations and operations_in_8idi():
    sd.monitor.append(aps.current)

    # suspend when current < 2 mA
    # resume 100s after current > 10 mA
    logger.info("Installing suspender for low APS current.")
    suspend_APS_current = bluesky.suspenders.SuspendFloor(aps.current, 2, resume_thresh=10, sleep=100)
    RE.install_suspender(suspend_APS_current)

    shutter = EpicsOnOffShutter("8idi:Unidig1Bo13", name="shutter")

else:
    logger.warning("!"*30)
    if operations_in_8idi():
        logger.warning("Session started when APS not operating.")
    else:
        logger.warning("Session started when 8_ID-I is not operating.")
    logger.warning("Using simulator 'shutter'.")
    logger.warning("!"*30)
    # simulate a shutter (no hardware required)
    shutter = SimulatedApsPssShutterWithStatus(name="shutter", labels=["shutter", "simulator"])
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
lakeshore = LS336Device("8idi:LS336:TC4:", name="lakeshore", labels=["heater", "Lakeshore"])

T_A = lakeshore.loop1.temperature
T_SET = lakeshore.loop1.target


class ModifiedEpidRecord(APS_synApps.EpidRecord):
    clock_ticks = None

pid1 = ModifiedEpidRecord("8idi:pid1", name="pid1", labels=["pid",])
pid2 = ModifiedEpidRecord("8idi:pid2", name="pid2", labels=["pid",])


preamps = PreampDevice(name="preamps")
