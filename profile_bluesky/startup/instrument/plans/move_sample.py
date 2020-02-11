
"""
Bluesky plans to move the sample stage and actuators
"""

__all__ = """
    movesample
    movesamx
    movesamz
    move_pind1_in
    move_pind1_out
    move_pind2_in
    move_pind2_out
    move_pind4z_in
    move_pind4z_out
""".split()

from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plan_stubs as bps
from ..devices import samplestage
from ..devices import actuator_pind1, actuator_pind2, actuator_flux


def movesample():
    yield from samplestage.movesample()


def movesamx():
    yield from samplestage.movesamx()


def movesamz():
    yield from samplestage.movesamz()


def move_pind1_in():
    yield from bps.mv(actuator_pind1, "IN")


def move_pind1_out():
    yield from bps.mv(actuator_pind1, "OUT")


def move_pind2_in():
    yield from bps.mv(actuator_pind2, "IN")


def move_pind2_out():
    yield from bps.mv(actuator_pind2, "OUT")


def move_pind4z_in():
    yield from bps.mv(actuator_flux, "IN")


def move_pind4z_out():
    yield from bps.mv(actuator_flux, "OUT")
