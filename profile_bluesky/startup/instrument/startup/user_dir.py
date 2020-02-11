
"""
support a .ipython/user directory for user files
"""

__all__ = []

import IPython.paths
import os
import sys

from ..session_logs import logger
logger.info(__file__)

user_dir = os.path.join(
        IPython.paths.get_ipython_dir(), 
        "user"
    )
sys.path.append(user_dir)

logger.info(f"User code directory: {user_dir}")
del user_dir
