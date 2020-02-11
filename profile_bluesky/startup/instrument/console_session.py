
"""
configure for data collection in a console session
"""

from .session_logs import *
logger.info(__file__)

from .mpl.console import *

# # are our soft IOCs running?
# logger.info("check if soft IOCs are running")
# from .iocs.check_iocs import *

logger.info("bluesky framework")

from .framework import *
from .devices import *
# TODO:
# from .plans import *
# from .utils import *

# from apstools.utils import device_read2table
# from apstools.utils import print_RE_md
# from apstools.utils import show_ophyd_symbols
