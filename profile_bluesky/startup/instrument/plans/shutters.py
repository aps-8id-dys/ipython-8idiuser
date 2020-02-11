
"""
Bluesky plans to use the shutters
"""

__all__ = """
    bb
    blockbeam
    block_directbeam_common
    sb
    showbeam
""".strip()

from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plan_stubs as bps
from ..devices import att1, att2, shutter


def bb():
    """block beam"""
    yield from bps.mv(shutter, "close")

blockbeam = bb  # alias

def sb():
    """show beam"""
    yield from bps.mv(shutter, "open")

showbeam = sb   # alias

def block_directbeam_common():
    yield from bps.mv(
        att1, 15,
        att2, 15,
    )
