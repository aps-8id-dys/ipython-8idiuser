
"""
Bluesky plans to move the sample stage and actuators
"""

__all__ = """
    lineup
    tw
""".strip()

from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plans as bp
from bluesky import plan_stubs as bps
from ..framework import bec
from ophyd.scaler import ScalerCH, ScalerChannel
import pyRestTable


def tw(counter, motor, delta):
    """
    maximize a positioner using a motor and reading a scaler channel

    In SPEC, the `tw` command initiates an interactive session.
    Automate that here, if possible.
    """
    # Usage:  tw mot [mot2 ...] delta [delta2 ...] [count_time]
    raise NotImplementedError("Need to write the Bluesky tw() plan")


def lineup(counter, axis, minus, plus, npts, time_s=0.1, peak_factor=4, width_factor=0.8,_md={}):
    """
    lineup and center a given axis, relative to current position

    PARAMETERS
    
    counter : Signal or scaler channel object
        detector or Signal to be maximized
    
    axis : movable
        Signal or EpicsMotor to use for alignment, the independent axis
    
    minus : float
        first point of scan at this offset from starting position
    
    plus : float
        last point of scan at this offset from starting position
    
    npts : int
        number of data points in the scan
    
    time_s : float (default: 0.1)
        count time per step
    
    peak_factor : float (default: 4)
        maximum must be greater than 'peak_factor'*minimum
    
    width_factor : float (default: 0.8)
        fwhm must be less than 'width_factor'*plot_range

    EXAMPLE:

        RE(lineup(diode, foemirror.theta, -30, 30, 30, 1.0))
    """
     # first, determine if counter is part of a ScalerCH device
    scaler = None
    obj = counter.parent
    if isinstance(counter.parent, ScalerChannel):
        if hasattr(obj, "parent") and obj.parent is not None:
            obj = obj.parent
            if hasattr(obj, "parent") and isinstance(obj.parent, ScalerCH):
                scaler = obj.parent

    if scaler is not None:
        old_sigs = scaler.stage_sigs
        scaler.stage_sigs["preset_time"] = time_s
        scaler.select_channels([counter.name])

    if hasattr(axis, "position"):
        old_position = axis.position
    else:
        old_position = axis.get()

    def peak_analysis():
        aligned = False
        if counter.name in bec.peaks["cen"]:
            table = pyRestTable.Table()
            table.labels = ("key", "value")
            table.addRow(("axis", axis.name))
            table.addRow(("detector", counter.name))
            table.addRow(("starting position", old_position))
            for key in bec.peaks.ATTRS:
                table.addRow((key, bec.peaks[key][counter.name]))
            logger.info(f"alignment scan results:\n{table}")

            lo = bec.peaks["min"][counter.name][-1]  # [-1] means detector
            hi = bec.peaks["max"][counter.name][-1]  # [0] means axis
            fwhm = bec.peaks["fwhm"][counter.name]
            final = bec.peaks["cen"][counter.name]

            ps = list(bec._peak_stats.values())[0][counter.name]    # PeakStats object
            # get the X data range as received by PeakStats
            x_range = abs(max(ps.x_data) - min(ps.x_data))

            if final is None:
                logger.error(f"centroid is None")
                final = old_position
            elif fwhm is None:
                logger.error(f"FWHM is None")
                final = old_position
            elif hi < peak_factor*lo:
                logger.error(f"no clear peak: {hi} < {peak_factor}*{lo}")
                final = old_position
            elif fwhm > width_factor*x_range:
                logger.error(f"FWHM too large: {fwhm} > {width_factor}*{x_range}")
                final = old_position
            else:
                aligned = True
            
            logger.info(f"moving {axis.name} to {final}  (aligned: {aligned})")
            yield from bps.mv(axis, final)
        else:
            logger.error("no statistical analysis of scan peak!")
            yield from bps.null()

        # too sneaky?  We're modifying this structure locally
        bec.peaks.aligned = aligned
        bec.peaks.ATTRS =  ('com', 'cen', 'max', 'min', 'fwhm')

    md = dict(_md)
    md["purpose"] = "alignment"
    yield from bp.rel_scan([counter], axis, minus, plus, npts, md=md)
    yield from peak_analysis()

    if bec.peaks.aligned:
        # again, tweak axis to maximize
        md["purpose"] = "alignment - fine"
        fwhm = bec.peaks["fwhm"][counter.name]
        yield from bp.rel_scan([counter], axis, -fwhm, fwhm, npts, md=md)
        yield from peak_analysis()

    if scaler is not None:
        scaler.select_channels()
        scaler.stage_sigs = old_sigs
