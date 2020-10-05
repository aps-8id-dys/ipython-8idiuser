
"""
email notices
"""


__all__ = [
    'email_notices',
]


from ..session_logs import logger
logger.info(__file__)

from apstools.utils import EmailNotifications

SENDER_EMAIL = "8idiuser@aps.anl.gov"
email_notices = EmailNotifications(SENDER_EMAIL)
email_notices.add_addresses(
    "qzhang234@anl.gov",
    "sureshn@anl.gov",
    "kswitalski@anl.gov",
    # add as FYI for Bluesky support:
    "jemian@anl.gov",
)
