
"""
fix a problem with the ``wa`` magic

see: https://github.com/aps-8id-dys/ipython-8idiuser/issues/201
"""


__all__ = ["LocalBlueskyMagics",]


from ..session_logs import logger
logger.info(__file__)


# from : ~/.conda/envs/bluesky_2020_9/lib/python3.8/site-packages/bluesky/magics.py

from bluesky.magics import _print_devices
from bluesky.magics import _print_positioners
from bluesky.magics import BlueskyMagics
from bluesky.magics import get_labeled_devices
from IPython.core.magic import magics_class, line_magic
from ophyd.utils import DisconnectedError


def is_positioner(dev):
    """fix to handle if dev is disconnected"""
    try:
        verdict = hasattr(dev, 'position')
    except DisconnectedError:
        verdict = False
    return verdict


@magics_class
class LocalBlueskyMagics(BlueskyMagics):
    """
    IPython magics for bluesky.

    To install:

    >>> ip = get_ipython()
    >>> ip.register_magics(MyBlueskyMagics)

    """

    @line_magic
    def wa(self, line):
        "List positioner info. 'wa' stands for 'where all'."
        # If the deprecated BlueskyMagics.positioners list is non-empty, it has
        # been configured by the user, and we must revert to the old behavior.
        if type(self).positioners:
            if line.strip():
                positioners = eval(line, self.shell.user_ns)
            else:
                positioners = type(self).positioners
            if len(positioners) > 0:
                _print_positioners(positioners, precision=self.FMT_PREC)
        else:
            # new behaviour
            devices_dict = get_labeled_devices(user_ns=self.shell.user_ns)
            if line.strip():
                if '[' in line or ']' in line:
                    raise ValueError("It looks like you entered a list like "
                                     "`%wa [motors, detectors]` "
                                     "Magics work a bit differently than "
                                     "normal Python. Enter "
                                     "*space-separated* labels like "
                                     "`%wa motors detectors`.")
                # User has provided a white list of labels like
                # %wa label1 label2
                labels = line.strip().split()
            else:
                # Show all labels.
                labels = list(devices_dict.keys())
            for label in labels:
                print(label)
                try:
                    devices = devices_dict[label]
                    all_children = [(k, getattr(obj, k))
                                    for _, obj in devices
                                    for k in getattr(obj, 'read_attrs', [])]
                except KeyError:
                    print('<no matches for this label>')
                    continue
                # Search devices and all their children for positioners.
                positioners = [dev for _, dev in devices + all_children
                               if is_positioner(dev)]
                if positioners:
                    _print_positioners(positioners, precision=self.FMT_PREC,
                                       prefix=" "*2)
                    print()  # blank line
                # Just display the top-level devices in the namespace (no
                # children).
                _print_devices(devices, prefix=" "*2)
                print()  # blank line


from IPython import get_ipython
ip = get_ipython()
ip.register_magics(LocalBlueskyMagics)
