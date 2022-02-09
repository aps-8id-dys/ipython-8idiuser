
# Users can keep adding plans to the file

from instrument.framework import bec, RE
from instrument.devices import lakeshore, flyscan, rigaku
from instrument.plans import AD_Acquire, movesample, select_RIGAKU
from bluesky import plans as bp
from bluesky import plan_stubs as bps
from instrument.collection import *
from instrument.devices import aps
from instrument.plans.flyscan import flyscan_spinner

import numpy as np

RE(select_RIGAKU())

rigaku.qmap_file = 'qzhang20201217_Rq1_Log_S270_D27.h5'


def repeat_acq(areadet=None, 
               file_header='F', 
               acq_rep=3, 
               sample_name='None', 
               Temp_list=[25],
               att_value=0,
               FLY_YES_NO = 'False',
               samx_cen = 'None',
               samz_cen = 'None'):

    bec.disable_plots()
    bec.disable_table()

    logger.setLevel(logging.INFO)

    yield from bps.mvr(dm_pars.ARun_number, 1)
    yield from bps.mv(att,att_value)


# Comment out these two lines to prevent moving the 4 m detector stage

    # yield from bps.mv(detu.x, -40.2)
    # yield from bps.mv(detu.z, 152.0)

    areadet = areadet or rigaku
    acq_header = f'{file_header}{int(dm_pars.ARun_number.get()):03d}'

    samx_num = 20
    samz_num = 40

    samx_list = np.linspace(samx_cen-0.1, samx_cen+0.1, num=samx_num)
    samz_list = np.linspace(samz_cen-0.1, samz_cen+0.1, num=samz_num)
 
    for ii in range(acq_rep): 
        
        pos_index = np.mod(ii,samx_num*samz_num)
        # yield from bps.mv(
        #     samplestage.x, samx_list[np.mod(pos_index,samx_num)],
        #     samplestage.z, samz_list[int(np.floor(pos_index/samx_num))]
        # )
        
        acq_name = f'{acq_header}_{ii+1:05}_att{att_value:02}_{sample_name}'

        logger.info(acq_name)

        if FLY_YES_NO == True:
            logger.info('Running the Fly Stage')
            yield from flyscan_spinner(8, 8+0.04*2.5, 0.1)

        print(acq_name)

        yield from AD_Acquire(
            rigaku,
            acquire_time=19.00e-6,
            acquire_period=19.00e-6,
            num_images=100000,
            file_name=acq_name,
            submit_xpcs_job=True,
            atten=None,
            # this is the path to where the metadata file will be stored
            path=f'/home/8ididata/{aps.aps_cycle.get()}/demo202101/',
            md={})

    bec.enable_plots()
    bec.enable_table()



def multi_capil():

    post_align()

    x0 = 0
    z0 = 0

    yield from repeat_acq(sample_name='Test',att_value=0,acq_rep=20000,samx_cen=0,samz_cen=0)

