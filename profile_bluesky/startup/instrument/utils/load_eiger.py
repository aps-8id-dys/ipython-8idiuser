""" Loads a new eiger device
Code borrowed from Gilberto:
https://github.com/APS-4ID-POLAR/ipython-polar/blob/master/profile_bluesky/startup/instrument/utils/load_eiger.py
"""

from ..devices.ad_eiger import EigerDetector
from ..framework import sd
from ..session_logs import logger
logger.info(__file__)

__all__ = ['load_eiger']


def load_eiger(
    pv="dp_eiger_xrd92:",
    write_image_path="",
    read_image_path=""
):

    logger.info("-- Loading Eiger detector --")
    eiger = EigerDetector(
        pv,
        write_image_path=write_image_path,
        read_image_path=read_image_path,
        name="eiger"
    )

    # TODO: Should we have this? It can create problems when eiger is not used.
    # sd.baseline.append(eiger)

    eiger.wait_for_connection(timeout=10)
    # This is needed otherwise .get may fail!!!

    # TODO: Are we using rois and stats?
    logger.info("Setting up ROI and STATS defaults ...  ")
    for name in eiger.component_names:
        if "roi" in name:
            roi = getattr(eiger, name)
            roi.wait_for_connection(timeout=10)
            roi.nd_array_port.put("EIG")
        if "stats" in name:
            stat = getattr(eiger, name)
            stat.wait_for_connection(timeout=10)
            stat.nd_array_port.put(f"ROI{stat.port_name.get()[-1]}")
    logger.info("Done!")

    logger.info("Setting up defaults kinds ...  ")
    eiger.default_kinds()
    logger.info("Done!")
    logger.info("Setting up default settings ...  ")
    eiger.default_settings()
    logger.info("Done!")
    logger.info("All done!")
    return eiger