logger.info(__file__)

"""local, custom Bluesky plans (scans)"""

# a place to store various preset values for the instrument
presets = {
    "pind1z" : {"in": 0.0, "out": 0.0},  # TODO: what values?
    "pind2z" : {"in": 0.0, "out": 0.0},  # TODO: what values?
}

def pind1z_in():
    yield from bps.mv(pind1z, presets["pindz1"]["in"])

def pind1z_out():
    yield from bps.mv(pind1z, presets["pindz1"]["out"])

def pind2z_in():
    yield from bps.mv(pind2z, presets["pindz2"]["in"])

def pind2z_out():
    yield from bps.mv(pind2z, presets["pindz2"]["out"])

def diodes_in():
    "move ALL the diode in"
    yield from bps.mv(
        pind1z, presets["pindz1"]["in"],
        pind2z, presets["pindz2"]["in"],
    )

def diodes_out():
    "move ALL the diode out"
    yield from bps.mv(
        pind1z, presets["pindz1"]["out"],
        pind2z, presets["pindz2"]["out"],
    )
