
"""
Enhance the apstools.utils.listruns() utility
"""

# NOTE: added to apstools 2020-02-28, no need to keep if we update local apstools

__all__ = """
    lambda_test
""".strip()

from instrument.session_logs import logger
logger.info(__file__)

from apstools.utils import ipython_shell_namespace
from apstools.utils import _rebuild_scan_command
import datetime
import pyRestTable

def listruns(
        num=20, keys=[], printing=True,
        show_command=True, db=None,
        exit_status=None,
        **db_search_terms):
    """
    make a table of the most recent runs (scans)

    PARAMETERS

    num : int
        Make the table include the ``num`` most recent runs.
        (default: ``20``)
    keys : [str]
        Include these additional keys from the start document.
        (default: ``[]``)
    printing : bool
        If True, print the table to stdout
        (default: ``True``)
    show_command : bool
        If True, show the (reconstructed) full command,
        but truncate it to no more than 40 characters)
        (note: This command is reconstructed from keys in the start
        document so it will not be exactly as the user typed.)
        (default: ``True``)
    db : object
        Instance of ``databroker.Broker()``
        (default: ``db`` from the IPython shell)
    db_search_terms : dict
        Any additional keyword arguments will be passed to
        the databroker to refine the search for matching runs.

    RETURNS

    object:
        Instance of ``pyRestTable.Table()``

    EXAMPLE::

        In [2]: from apstools import utils as APS_utils

        In [3]: APS_utils.listruns(num=5, keys=["proposal_id","pid"])
        ========= ========================== ======= ======= ======================================== =========== ===
        short_uid date/time                  exit    scan_id command                                  proposal_id pid
        ========= ========================== ======= ======= ======================================== =========== ===
        5f2bc62   2019-03-10 22:27:57.803193 success 3       fly()
        ef7777d   2019-03-10 22:27:12.449852 success 2       fly()
        8048ea1   2019-03-10 22:25:01.663526 success 1       scan(detectors=['calcs_calc2_val'],  ...
        83ad06d   2019-03-10 22:19:14.352157 success 4       fly()
        b713d46   2019-03-10 22:13:26.481118 success 3       fly()
        ========= ========================== ======= ======= ======================================== =========== ===

        In [100]: listruns(keys=["file_name",], since="2020-02-06", until="2020-02-07", num=10, plan_name="lambda_test", exit_status="success")
            ...:
        ========= ========================== ======= ======= ======================================== ==============================
        short_uid date/time                  exit    scan_id command                                  file_name
        ========= ========================== ======= ======= ======================================== ==============================
        efab384   2020-02-06 11:21:36.129510 success 5081    lambda_test(detector_name=lambdadet, ... C042_Latex_Lq0_001
        394a20a   2020-02-06 10:32:07.525558 success 5072    lambda_test(detector_name=lambdadet, ... B041_Aerogel_Translate_Lq0_001
        aeea69b   2020-02-06 10:31:27.522871 success 5071    lambda_test(detector_name=lambdadet, ... B040_Aerogel_Translate_Lq0_001
        b39813a   2020-02-06 10:27:16.267097 success 5069    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_005
        0651cb6   2020-02-06 10:27:02.070575 success 5068    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_004
        63897f8   2020-02-06 10:26:47.770677 success 5067    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_003
        188d31a   2020-02-06 10:26:33.230039 success 5066    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_002
        9907451   2020-02-06 10:26:19.048433 success 5065    lambda_test(detector_name=lambdadet, ... A038_Aerogel_Lq0_001
        ========= ========================== ======= ======= ======================================== ==============================

        Out[100]: <pyRestTable.rest_table.Table at 0x7f004e4d4898>

    *new in apstools release 1.1.10*
    """
    db = db or ipython_shell_namespace()["db"]

    if show_command:
        labels = "scan_id  command".split() + keys
    else:
        labels = "scan_id  plan_name".split() + keys

    table = pyRestTable.Table()
    table.labels = "short_uid   date/time  exit".split() + labels

    if len(db_search_terms) > 0:
        # TODO: Can this be more efficient to extract `num` runs?
        runs = list(db(**db_search_terms))[-abs(num):]
    else:
        runs = db[-abs(num):]
    for h in runs:
        if (
                exit_status is not None 
                and 
                h.stop.get("exit_status") != exit_status):
            continue
        row = [
            h.start["uid"][:7],
            datetime.datetime.fromtimestamp(h.start['time']),
            h.stop.get("exit_status", "")
            ]
        for k in labels:
            if k == "command":
                command = _rebuild_scan_command(h.start)
                command = command[command.find(" "):].strip()
                maxlen = 40
                if len(command) > maxlen:
                    suffix = " ..."
                    command = command[:maxlen-len(suffix)] + suffix
                row.append(command)
            else:
                row.append(h.start.get(k, ""))
        table.addRow(row)

    if printing:
        print(table)
    return table
