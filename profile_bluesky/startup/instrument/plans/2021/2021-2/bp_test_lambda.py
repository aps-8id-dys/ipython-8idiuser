
from instrument.framework import bec, RE
from instrument.devices import lakeshore, flyscan, adrigaku
from instrument.plans import AD_Acquire, movesample, select_RIGAKU
from bluesky import plans as bp
from bluesky import plan_stubs as bps
from instrument.collection import *
from instrument.devices import aps

import numpy as np


dm_pars.transfer.put('xpcs8-01-Lambda')
dm_pars.analysis.put('xpcs8-02-Lambda')
dm_pars.qmap_file.put('weichen202107a_qmap_Lq2_S270_D54.h5')


def repeat_lambda_acq(file_header='H', 
               acq_rep=3, 
               sample_name='Test', 
               Temp_list=[25],
               att_value=0,
               samx_cen = 0,
               samz_cen = 0):

    bec.disable_plots()
    bec.disable_table()

    logger.setLevel(logging.INFO)

    yield from bps.mvr(dm_pars.ARun_number, 1)
    # yield from bps.mv(att,att_value)

    acq_header = f'{file_header}{int(dm_pars.ARun_number.get()):03d}'

    samx_num = 20
    samz_num = 40

    samx_list = np.linspace(samx_cen-0.0, samx_cen+0.0, num=samx_num)
    samz_list = np.linspace(samz_cen-0.0, samz_cen+0.0, num=samz_num)

    for ii in range(acq_rep): 
        
        pos_index = np.mod(ii,samx_num*samz_num)
        # yield from bps.mv(
        #     samplestage.x, samx_list[np.mod(pos_index,samx_num)],
        #     samplestage.z, samz_list[int(np.floor(pos_index/samx_num))]
        # )
        
        acq_name = f'{acq_header}_{ii+1:05}_att{att_value:02}_{sample_name}'

        logger.info(acq_name)
        print(acq_name)

        yield from AD_Acquire(
            lambdadet,
            file_name=acq_name,
            acquire_time=1e-1,
            acquire_period=1e-1,
            num_images=50,
            path='/home/8ididata/2021-2/rigaku202108/',
            submit_xpcs_job=True,
            atten=att_value,
            md={})

    bec.enable_plots()
    bec.enable_table()