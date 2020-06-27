
"""
configure for data collection in a console session
"""

from .session_logs import *
logger.info(__file__)

from .mpl import *

logger.info("bluesky framework")

from .framework import *
from .devices import *
from .plans import *
from .utils import *

from apstools.utils import *

# ensure we return the session logger to the console
from .session_logs import logger
