
"""
Bluesky plans to use the EPICS PV registers
"""

__all__ = """
    get_detector_number_by_name
    pv_reg_read
    pv_reg_write
    beam_params_backup
    beam_params_restore
    select_LAMBDA
    select_RIGAKU
""".split()

from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plan_stubs as bps
from ..devices import detu, detd, dm_pars, dm_workflow
from ..devices import shutter_mode, shutter_override, soft_glue
from ophyd import EpicsSignal
import pyRestTable
from .shutters import blockbeam


PV_REG_MAP = {
    "template": "8idi:Reg%d",
    "detector_pv" : "8idi:Reg2",
    "registers/detector": 10,
    "highest register": 200,
    "regpv_start": {
        "current" : 11,
        "LAMBDA" : 91,
        "RIGAKU500K_NoGap" : 141,
    },
    "detectors" : {
        25 : "LAMBDA",
        46 : "RIGAKU500K_NoGap",
    },
    "burst mode pv" : "8idi:Reg124",    # added May 2019
}

PV_REG_MAP["registers"] = [     # each register is a signal
    EpicsSignal(
        PV_REG_MAP["template"] % (i+1), 
        name="pv_reg%d" % (i+1)
        )
    for i in range(PV_REG_MAP["highest register"])
    ]

PV_REG_MAP["registers"].insert(0, None)     # offset since no 8idi:Reg0


def get_detector_number_by_name(detName):
    global PV_REG_MAP
    if detName in PV_REG_MAP["detectors"].values():
        for detNum, k in PV_REG_MAP["detectors"].items():
            if k == detName:
                return detNum


def pv_reg_read(num):
    """read a value from PV register (indexed by number)"""
    global PV_REG_MAP
    register = PV_REG_MAP["registers"][num]
    if register is not None:
        return register.get()


def pv_reg_write(num, value):
    """read a value to PV register (indexed by number)"""
    global PV_REG_MAP
    register = PV_REG_MAP["registers"][num]
    if register is not None:
        yield from bps.mv(register, value)


def beam_params_backup():
    """
    copy detector registers from current to detector
    """
    global PV_REG_MAP
    detNum = dm_pars.detNum.get()
    detName = PV_REG_MAP["detectors"].get(detNum)
    logger.debug(f"Backing up {detName} detector Beam Params")

    if detName is None:
        msg = f"Unknown detector number {detNum}"
        msg += f" in EPICS PV register {dm_pars.detNum.pvname}"
        raise ValueError(msg)

    offset = PV_REG_MAP["regpv_start"][detName]
    offset_current = PV_REG_MAP["regpv_start"]["current"]
    t = pyRestTable.Table()
    t.addLabel("value")
    t.addLabel("from")
    t.addLabel("to")
    for i in range(PV_REG_MAP["registers/detector"]):
        target = PV_REG_MAP["registers"][i + offset]
        source = PV_REG_MAP["registers"][i + offset_current]
        t.addRow((source.get(), source.pvname, target.pvname))
        yield from bps.mv(target, source.get())
    logger.debug(f"Detector {detName} Beam Params are Backed up\n{t}")


def beam_params_restore():
    """
    copy detector registers from detector to current
    """
    global PV_REG_MAP
    detNum = dm_pars.detNum.get()
    detName = PV_REG_MAP["detectors"].get(detNum)

    if detName is None:
        raise ValueError(
            f"Unknown detector number {detNum}"
            f" in EPICS PV register {dm_pars.detNum.pvname}"
        )

    offset = PV_REG_MAP["regpv_start"][detName]
    offset_current = PV_REG_MAP["regpv_start"]["current"]
    t = pyRestTable.Table()
    t.addLabel("value")
    t.addLabel("from")
    t.addLabel("to")
    for i in range(PV_REG_MAP["registers/detector"]):
        source = PV_REG_MAP["registers"][i + offset]
        target = PV_REG_MAP["registers"][i + offset_current]
        t.addRow((source.get(), source.pvname, target.pvname))
        yield from bps.mv(target, source.get())
        # logger.debug(f"{target.pvname} = {target.get()}")
    logger.debug(f"Detector {detName} Beam Params are restored\n{t}")


def select_LAMBDA(distance=None):
    """
    select the LAMBDA detetcor
    """
    yield from beam_params_backup()
    yield from bps.mv(
        dm_pars.detNum, get_detector_number_by_name("LAMBDA"),
        dm_pars.detector_distance, 3930.00, #moved sample 7 inches closer to detector
        dm_pars.airgap, 240.00,
    )
    # logger.info(f"******** detector number {dm_pars.detNum.get()} ************************")
    yield from beam_params_restore()
    yield from bps.sleep(1)
    yield from blockbeam()
    
    logger.info("Moving LAMBDA PAD to the direct beam position")

    distance = distance or "4 m"
    if distance == "4 m":
        # logger.debug(f"ccdx0={dm_pars.ccdx0.get()}, ccdz0={dm_pars.ccdz0.get()}")
        yield from bps.mv(
            detu.x, dm_pars.ccdx0.get(),
            detu.z, dm_pars.ccdz0.get(),
        )
        # yield from bps.mv(
        #     detu.x, 214.10,
        #     detu.z, 36.95,
        # )
        # logger.debug(f"detu.x={detu.x.position}, detu.z={detu.z.position}")
    elif distance == "8 m":
        yield from bps.mv(
            detd.x, dm_pars.ccdx0.get(),
            detd.z, dm_pars.ccdz0.get(),
        )
        # yield from bps.mv(
        #     detd.x, 127.53,
        #     detd.z, 15.55,
        # )

    yield from bps.mv(shutter_override, 1)
    yield from blockbeam()

    yield from bps.mv(
        # NOTE: these are all stringout records!  Use a str!
        soft_glue.send_ext_pulse_tr_sig_to_trig, "1",
        # soft_glue.set_shtr_sig_pulse_tr_mode, "0",
        # soft_glue.send_det_sig_pulse_tr_mode, "0",
    )

	# TODO: needs some planning here, see below
    # def xpcs_pre_start \'xpcs_pre_start_LAMBDA\';
	# def user_xpcs_loop \'user_xpcs_loop_LAMBDA\';

    yield from bps.mv(shutter_mode, "1UFXC")    # "align" mode

    dm_workflow.transfer = "xpcs8-01-Lambda"
    dm_workflow.analysis = "xpcs8-02-Lambda"
    yield from bps.mv(
        dm_pars.burst_mode_state, 0,    # 2019-05, set default status
        dm_pars.transfer, dm_workflow.transfer,
        dm_pars.analysis, dm_workflow.analysis,
    )


def select_RIGAKU():
    """
    select the RIGAKU detetcor
    """
    yield from beam_params_backup()
    yield from bps.mv(
        dm_pars.detNum, get_detector_number_by_name("RIGAKU500K_NoGap"),
        dm_pars.detector_distance, 3930.00, #moved sample 7 inches closer to detector
        dm_pars.airgap, 100.00,
    )
    logger.info(f"******** detector number {dm_pars.detNum.get()} ************************")
    yield from beam_params_restore()
    yield from bps.sleep(1)
    yield from blockbeam()
    
    logger.info("Moving RIGAKU to the direct beam position")

    # logger.debug(f"ccdx0={dm_pars.ccdx0.get()}, ccdz0={dm_pars.ccdz0.get()}")
    yield from bps.mv(
        detu.x, dm_pars.ccdx0.get(),
        detu.z, dm_pars.ccdz0.get(),
    )
    # logger.debug(f"detu.x={detu.x.position}, detu.z={detu.z.position}")

    yield from bps.mv(shutter_override, 1)
    yield from blockbeam()

    # TODO: needs some planning here, see below
    # def xpcs_pre_start \'xpcs_pre_start_RIGAKU\';
    # def user_xpcs_loop \'user_xpcs_loop_RIGAKU\';

    dm_workflow.transfer = "xpcs8-01-stage"
    dm_workflow.analysis = "xpcs8-02-Rigaku-bin-stage"
    yield from bps.mv(
        dm_pars.burst_mode_state, 0,    # 2019-05, set default status
        dm_pars.transfer, dm_workflow.transfer,
        dm_pars.analysis, dm_workflow.analysis,
    )
