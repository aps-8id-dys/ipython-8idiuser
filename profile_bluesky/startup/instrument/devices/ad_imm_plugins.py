"""
Area Detector IMM Plugin support for ophyd
"""

__all__ = """
    IMM_DeviceMixinBase
    IMMnLocal
    IMMoutLocal
""".split()

from ..session_logs import logger

logger.info(__file__)

from ..framework import db
from area_detector_handlers.handlers import HandlerBase
from bluesky import plan_stubs as bps
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
import numpy as np
import struct


class IMMnLocal(Device):
    """
    local interface to the IMM0, IMM1, & IMM2 plugins
    """

    capture = Component(EpicsSignalWithRBV, "Capture", kind="config")
    file_format = Component(
        EpicsSignalWithRBV, "NDFileIMM_format", string=True, kind="config"
    )
    num_captured = Component(EpicsSignalRO, "NumCaptured_RBV")


class IMMoutLocal(Device):
    """
    local interface to the IMMout plugin
    """

    # implement just the parts needed by our data acquisition
    auto_increment = Component(
        EpicsSignalWithRBV, "AutoIncrement", kind="config"
    )
    blocking_callbacks = Component(
        EpicsSignalWithRBV, "BlockingCallbacks", kind="config"
    )
    capture = Component(EpicsSignalWithRBV, "Capture", kind="config")
    enable = Component(
        EpicsSignalWithRBV, "EnableCallbacks", string=True, kind="config"
    )
    file_format = Component(
        EpicsSignalWithRBV, "NDFileIMM_format", string=True, kind="config"
    )
    file_name = Component(EpicsSignalWithRBV, "FileName", string=True, kind="config")
    file_number = Component(EpicsSignalWithRBV, "FileNumber", kind="config")
    file_path = Component(EpicsSignalWithRBV, "FilePath", string=True, kind="config")
    full_file_name = Component(
        EpicsSignalRO, "FullFileName_RBV", string=True, kind="config"
    )
    num_capture = Component(EpicsSignalWithRBV, "NumCapture", kind="config")
    num_captured = Component(EpicsSignalRO, "NumCaptured_RBV")
    num_pixels = Component(EpicsSignalRO, "NDFileIMM_num_imm_pixels_RBV", kind="config")

    unique_id = Component(EpicsSignalRO, "NDFileIMM_uniqueID_RBV")


class IMM_DeviceMixinBase(Device):
    """
    attributes used by area detectors using the IMM Plugin
    """

    immout = Component(IMMoutLocal, "IMMout:")
    imm0 = Component(IMMnLocal, "IMM0:")
    imm1 = Component(IMMnLocal, "IMM1:")
    imm2 = Component(IMMnLocal, "IMM2:")

    def setIMM_Cmprs(self):
        """
        Set all IMM plugins for compression.
        """
        # from SPEC macro: ccdset_compr_params_ad_Lambda
        for plugin in (self.imm0, self.imm1, self.imm2, self.immout):
            if plugin.file_format.get() not in (1, "IMM_Cmprs"):
                yield from bps.mv(
                    plugin.capture,
                    "Done",  # ('Done', 'Capture')
                    plugin.file_format,
                    "IMM_Cmprs",  # ('IMM_Raw', 'IMM_Cmprs')
                )

    def setIMM_Raw(self):
        """
        Set all IMM plugins for raw (uncompressed).
        """
        # from SPEC macro: ccdset_RawMode_params_ad_Lambda
        for plugin in (self.imm0, self.imm1, self.imm2, self.immout):
            if plugin.file_format.get() not in (0, "IMM_Raw"):
                yield from bps.mv(
                    plugin.capture,
                    "Done",  # ('Done', 'Capture')
                    plugin.file_format,
                    "IMM_Raw",  # ('IMM_Raw', 'IMM_Cmprs')
                )


# ----------------------------------------------------------------
#
# Setup support for the IMM data format (so databroker can read the files)

imm_headformat = "ii32s16si16siiiiiiiiiiiiiddiiIiiI40sf40sf40sf40sf40sf40sf40sf40sf40sf40sfffiiifc295s84s12s"

imm_fieldnames = [
    "mode",
    "compression",
    "date",
    "prefix",
    "number",
    "suffix",
    "monitor",
    "shutter",
    "row_beg",
    "row_end",
    "col_beg",
    "col_end",
    "row_bin",
    "col_bin",
    "rows",
    "cols",
    "bytes",
    "kinetics",
    "kinwinsize",
    "elapsed",
    "preset",
    "topup",
    "inject",
    "dlen",
    "roi_number",
    "buffer_number",
    "systick",
    "pv1",
    "pv1VAL",
    "pv2",
    "pv2VAL",
    "pv3",
    "pv3VAL",
    "pv4",
    "pv4VAL",
    "pv5",
    "pv5VAL",
    "pv6",
    "pv6VAL",
    "pv7",
    "pv7VAL",
    "pv8",
    "pv8VAL",
    "pv9",
    "pv9VAL",
    "pv10",
    "pv10VAL",
    "imageserver",
    "CPUspeed",
    "immversion",
    "corecotick",
    "cameratype",
    "threshhold",
    "byte632",
    "empty_space",
    "ZZZZ",
    "FFFF",
]


def readHeader(fp):
    bindata = fp.read(1024)

    imm_headerdat = struct.unpack(imm_headformat, bindata)
    imm_header = {}
    for k in range(len(imm_headerdat)):
        imm_header[imm_fieldnames[k]] = imm_headerdat[k]

    return imm_header


class IMMHandler(HandlerBase):
    def __init__(self, filename, frames_per_point):
        self.file = open(filename, "rb")
        self.frames_per_point = frames_per_point
        header = readHeader(self.file)
        self.rows, self.cols = header["rows"], header["cols"]
        self.is_compressed = bool(header["compression"] == 6)
        self.file.seek(0)
        self.toc = []  # (start byte, element count) pairs
        while True:
            try:
                header = readHeader(self.file)
                print("header rows and cols", header["rows"], header["cols"])
                cur = self.file.tell()
                payload_size = header["dlen"] * (6 if header["compression"] == 6 else 2)
                self.toc.append((cur, header["dlen"]))
                file_pos = payload_size + cur
                self.file.seek(file_pos)
                # Check for end of file.
                if not self.file.read(4):
                    break
                self.file.seek(file_pos)
            except Exception as err:
                raise IOError("IMM file doesn't seems to be of right type") from err

    def close(self):
        self.file.close()

    def __call__(self, index):
        logger.info(f"index: {index}")
        result = np.zeros((self.frames_per_point, self.rows * self.cols), np.uint32)
        for i in range(self.frames_per_point):
            # looping through plane 'i' of chunk 'index'
            start_byte, num_pixels = self.toc[index * self.frames_per_point + i]
            self.file.seek(start_byte)
            indexes = np.fromfile(self.file, dtype=np.uint32, count=num_pixels)
            values = np.fromfile(self.file, dtype=np.uint16, count=num_pixels)
            # if self.is_compressed:

            result[i, indexes] = values
            # else:
            #    result = dense_array
        return result.reshape(self.frames_per_point, self.rows, self.cols)


db.reg.register_handler("IMM", IMMHandler, overwrite=True)
