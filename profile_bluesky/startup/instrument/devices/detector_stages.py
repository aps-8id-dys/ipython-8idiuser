
"""
detector stages
"""

__all__ = ['detd', 'detu',]

from instrument.session_logs import logger
logger.info(__file__)

from ophyd import Component, Device, EpicsMotor


class DetStageUpstream(Device):  
    """
    Upstream detector stage at 4 m (the old 'ccdx' and 'ccdz')
    """    
    x = Component(EpicsMotor, '8idi:m90', labels=["motor", "det"])
    z = Component(EpicsMotor, '8idi:m91', labels=["motor", "det"])
  

class DetStageDownstream(Device):  
    """
    Downstream detector stage at 8 m (the old 'fccdx' and 'fccdz')
    """    
    x = Component(EpicsMotor, '8idi:m25', labels=["motor", "det"])
    z = Component(EpicsMotor, '8idi:m83', labels=["motor", "det"])


detu = DetStageUpstream(name="detu")
detd = DetStageDownstream(name="detd")
