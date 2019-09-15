print(__file__)

"""
configure logging
"""

_log_path = os.path.join(os.getcwd(), ".logs")
if not os.path.exists(_log_path):
    os.mkdir(_log_path)
CONSOLE_IO_FILE = os.path.join(_log_path, ".ipython_console.log")

# start logging console to file
# https://ipython.org/ipython-doc/3/interactive/magics.html#magic-logstart
from IPython import get_ipython
_ipython = get_ipython()
# %logstart -o -t .ipython_console.log "rotate"
_ipython.magic(f"logstart -o -t {CONSOLE_IO_FILE} rotate")


# pip install stdlogpj
import stdlogpj
logger = stdlogpj.standard_logging_setup(
    "bluesky-ipython-shell", "ipython_logger")

logger.warning('#'*60 + " startup")
logger.warning('logging started')
logger.warning(f'logging level = {logger.level}')

# logger.debug('example Debug message')
# logger.info('example Info message')
# logger.warning('example Warning message')
# logger.error('example Error message')
