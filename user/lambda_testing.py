
# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)

"""
test that we can run user ops continuously - use Lambda detector
"""

def lambda_test(num_iter=10):
    bec.disable_plots()
    bec.disable_table()
    bec.disable_baseline()

    for i in range(num_iter):
        if dm_pars.stop_before_next_scan.get() != 0:
            logger.info("received signal to STOP before next scan")
            yield from bps.mv(dm_pars.stop_before_next_scan, 0)
            break

        # increment the run number
        yield from bps.mvr(dm_pars.ARun_number, 1)
        file_name = f"A{dm_pars.ARun_number.value:03.0f}"

        yield from AD_Acquire(lambdadet, 
            acquire_time=0.1, acquire_period=0.11, 
            num_images=100, file_name=file_name,
            submit_xpcs_job=True,
            atten=None, path=None)

    bec.enable_baseline()
    bec.enable_table()
    bec.enable_plots()


def trubble():
    """
    demonstrate a problem when using bluesky 1.6.0rc3

    latest release (bluesky 1.4.1) does not raise tihs exception

    see: https://github.com/bluesky/bluesky/issues/1282
    """
    import databroker
    md = {
        "demonstrate": "trouble",
        "versions" : {
            "bluesky": bluesky.__version__,
            "ophyd": ophyd.__version__,
            "databroker": databroker.__version__,
        }
    }
    print(md)
    yield from bps.open_run(md=md)
    # FIXME: exception here
    """
    ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 139836100364096 and this is thread id 139834963904256.

    not a problem with bluesky 1.4.1
    exception with bluesky v1.6.0rc3 and master (2020-01-28)
    """
    yield from bps.create('primary')
    # dm_pars.ARun_number = Component(EpicsSignal, "8idi:Reg173")
    yield from bps.read(dm_pars.ARun_number)
    yield from bps.save()
    yield from bps.close_run()
