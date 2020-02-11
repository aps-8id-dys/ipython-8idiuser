
"""
configure for data collection in a console session
"""

from .session_logs import *
logger.info(__file__)

from .mpl.console import *

logger.info("bluesky framework")

from .framework import *
from .devices import *
from .plans import *
from .utils import *

from apstools.utils import device_read2table
from apstools.utils import print_RE_md
from apstools.utils import show_ophyd_symbols
