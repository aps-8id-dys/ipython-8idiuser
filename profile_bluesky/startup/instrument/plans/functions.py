
"""
various functions
"""

__all__ = ["taylor_series", ]

from instrument.session_logs import logger
logger.info(__file__)


def taylor_series(x, coefficients):
    """
    compute a Taylor series expansion at x
    
    a0 + x*(a1 + x*(a2+x*0)
    """
    v = 0
    for a in reversed(coefficients):
        v = v*x + a
    return v
