logger.info(__file__)

"""
support for APS data management
"""


class EpicsSignalDM(EpicsSignal):
    """custom class for Data Management metadata"""
    label = None
    h5address = None

