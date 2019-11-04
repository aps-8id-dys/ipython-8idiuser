logger.info(__file__)

"""local, custom Bluesky plans (scans)"""

from collections import namedtuple

# access by subscript or by name (obj[0]= same as obj.in)
in_out_tuple = namedtuple('in_out_tuple', 'in out')

class Presets:
    """
    various instrument settings and constants
    """
    pind1z = in_out_tuple(1, 0)  # TODO: what values?
    pind2z = in_out_tuple(1, 0)  # TODO: what values?
    pvFLUX_PIND = in_out_tuple(1, 0)

preset = Presets()


def pind1z_in():
    yield from bps.mv(pind1z, presets.pind1z.in)

def pind1z_out():
    yield from bps.mv(pind1z, presets.pind1z.out)

def pind2z_in():
    yield from bps.mv(pind2z, presets.pind2z.in)

def pind2z_out():
    yield from bps.mv(pind2z, presets.pind2z.out)

def pvFLUX_PIND_in():
    yield from bps.mv(pvFLUX_PIND, presets.pvFLUX_PIND.in)

def pvFLUX_PIND_out():
    yield from bps.mv(pvFLUX_PIND, presets.pvFLUX_PIND.out)

def diodes_in():
    "move ALL the diodes in"
    yield from bps.mv(
        pind1z, presets.pind1z.in,
        pind2z, presets.pind2z.in,
        pvFLUX_PIND, presets.pvFLUX_PIND.in,
    )

def diodes_out():
    "move ALL the diodes out"
    yield from bps.mv(
        pind1z, presets.pind1z.out,
        pind2z, presets.pind2z.out,
        pvFLUX_PIND, presets.pvFLUX_PIND.out,
    )
