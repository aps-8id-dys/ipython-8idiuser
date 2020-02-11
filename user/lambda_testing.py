
"""
test that we can run user ops continuously - use Lambda detector
"""

__all__ = """
    lambda_test
""".strip()

from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plan_stubs as bps
from instrument.devices import bec, detu, dm_pars, lambdadet
from instrument.plans import AD_Acquire, movesample


def lambda_test(num_iter=1, 
                acquire_time=0.1, 
                acquire_period=0.11,
                num_images=100,
                sample_name="test", 
                sample_prefix="A",
                sample_suffix="Lq0", 
                analysis_true_false=True):
    """
    test XPCS acquisition with the Lambda detector

    keep same arguments as similar Rigaku test
    """

    bec.disable_plots()
    bec.disable_table()
    bec.disable_baseline()

    lambdadet.cam.EXT_TRIGGER = 0
    lambdadet.cam.LAMBDA_OPERATING_MODE = 0
    

    # increment the run number
    yield from bps.mvr(dm_pars.ARun_number, 1)

    for i in range(num_iter):
        if dm_pars.stop_before_next_scan.get() != 0:
            logger.info("received signal to STOP before next scan")
            yield from bps.mv(dm_pars.stop_before_next_scan, 0)            
            break

        file_name = f"{sample_prefix}{dm_pars.ARun_number.get():03.0f}_{sample_name}_{sample_suffix}_{i+1:03.0f}"
        yield from movesample()

        lambdadet.qmap_file='richards202002_qmap_Lq0_S270_D54.h5'

        yield from bps.mv(
            detu.x, 213.8,
            detu.z, 36.85)

        yield from AD_Acquire(lambdadet, 
            acquire_time=acquire_time, acquire_period=acquire_period, 
            num_images=num_images, file_name=file_name,
            submit_xpcs_job=analysis_true_false,
            atten=None, path='/home/8-id-i/2020-1/bluesky/',
            md={"sample_name": sample_name})
        logger.info("diagnostic sleep")
        yield from bps.sleep(2) # diagnostic
        logger.info("-"*20 + " end of acquire")

    bec.enable_baseline()
    bec.enable_table()
    bec.enable_plots()
