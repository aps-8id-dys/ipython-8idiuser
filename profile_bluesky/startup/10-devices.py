logger.info(__file__)

"""local, custom Device definitions"""


class CompoundRefractiveLensDevice(Device):
    x = Component(EpicsSignal, '8idi:m65', labels=["motor", "crl", "optics"])
    # y = Component(EpicsSignal, '8idi:m68', labels=["motor", "crl", "optics"])
    z = Component(EpicsSignal, '8idi:m62', labels=["motor", "crl", "optics"])
    pitch = Component(EpicsSignal, '8idi:m67', labels=["motor", "crl", "optics"])
    yaw = Component(EpicsSignal, '8idi:m66', labels=["motor", "crl", "optics"])


class MonochromatorDevice(Device):
    monoE = Component(EpicsSignal, '8idimono:sm2', labels=["motor", "mono", "optics"])
    monoth = Component(EpicsSignal, '8idimono:sm1', labels=["motor", "mono", "optics"])
    piezo = Component(EpicsSignal, '8idimono:m4', labels=["motor", "mono", "optics"])
    monopic = Component(EpicsSignal, '8idimono:m1', labels=["motor", "mono", "optics"])
    nano = Component(EpicsSignal, '8idimono:m5', labels=["motor", "mono", "optics"])
