
# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)

"""
test that we can run user ops continuously - use Lambda detector
"""

def lambda_test(num_iter=10):
    for i in range(num_iter):
        if dm_pars.stop_before_next_scan.value != 0:
            logger.info("received signal to STOP before next scan")
            yield from bps.mv(dm_pars.stop_before_next_scan, 0)
            break

        yield from bps.mvr(dm_pars.ARun_number, 1)
        file_name = f"A{dm_pars.ARun_number.value:03.0f}"

        yield from AD_Acquire(lambdadet, 
            acquire_time=0.1, acquire_period=0.11, 
            num_images=100, file_name=file_name,
            submit_xpcs_job=True,
            atten=None, path=None)
