"""
Handler for the Eiger detector HDF5 files.
"""

from area_detector_handlers.handlers import AreaDetectorHDF5SingleHandler
from dask.array import from_array
from ..session_logs import logger
logger.info(__file__)


class EigerHDF5Handler(AreaDetectorHDF5SingleHandler):
    specs = (
        {"AD_HDF5_Eiger500k_APS8ID"} | AreaDetectorHDF5SingleHandler.specs
    )

    def __call__(self, point_number):
        return from_array(super().__call__(point_number))
