"""
AD_Acquire() detector base classes

This module provides base classes for detectors that can be used with
``instrument.plans.AD_Acquire()``.

This file describes the detector terms used by the ``AD_Acquire()``
plan.  Detectors should use the two Devices (`AD_AcquireDetectorBase`
and `AD_AcquireDetectorCamBase`) as mixin classes when constructing
the custom area detector support.
"""

__all__ = """
    AD_AcquireDetectorBase
    AD_AcquireDetectorCamBase
""".split()

from ..session_logs import logger

logger.info(__file__)


from bluesky import plan_stubs as bps
from ophyd import Device


class AD_AcquireDetectorBase(Device):
    """
    Detector interface to ``AD_Acquire()`` plan.

    Values provided here are either good defaults or definite errors if
    the subclass does not redefine them.
    """

    def staging_setup_DM(self, *args, **kwargs):
        """
        setup the detector's stage_sigs for acquisition with the DM workflow

        from DM_DeviceMixinAreaDetector

        args: file_path, file_name, num_images, acquire_time, acquire_period
        """
        if len(args) != 5:
            raise IndexError(f"expected 5 parameters, received {len(args)}: args={args}")
        raise NotImplementedError("Must implement in detector cam-specific subclass.")

    @property
    def images_received(self):
        """
        Return the number (int) of images captured.

        suggestion:  ``self.immout.num_captured.get()``
        """
        raise NotImplementedError("Must implement in detector-specific subclass.")


class AD_AcquireDetectorCamBase(Device):
    """
    Detector cam-module interface to ``AD_Acquire()`` plan.

    Values provided here are either good defaults or definite errors if
    the subclass does not redefine them.
    """

    def setup_modes(self, num_triggers):
        """
        Set up modes accordingly, based on self.EXT_TRIGGER.

        This will be executed by ``AD_Acquire()`` as a bluesky plan.

        PARAMETERS

        num_triggers (*int*):
            number of trigger events to be received
        """
        yield from bps.null()  # at least must yield *some* bluesky message
        raise NotImplementedError("Must implement in detector-specific subclass.")

    def setTime(self, exposure_time, exposure_period):
        """
        Set exposure time and period.
        """
        yield from bps.mv(self.acquire_time, exposure_time)
        yield from bps.mv(self.acquire_period, exposure_period)
