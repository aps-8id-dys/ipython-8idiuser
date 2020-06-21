
# Users can keep adding plans to the file

from instrument.framework import bec
from instrument.devices import lakeshore
from instrument.plans import AD_Acquire, movesample
from instrument.collection import *

import numpy as np


def raster_acq():
    
    acq_header = 'A200'
    acq_rep = 11
    sample_name = 'Silica-D100'


    samx_min = -1
    samx_max = 1
    samx_num = 3

    samz_min = -0.5
    samz_max = 0.5
    samz_num = 3

    Temp_list = [25, 26]

    samx_list = np.linspace(samx_min, samx_max, num=samx_num)
    samz_list = np.linspace(samz_min, samz_max, num=samz_num)


    for kk in range(len(Temp_list)):   
        yield from bps.mv(
            lakeshore.loop1.target, Temp_list[kk],  # te $Temp
            lakeshore.loop1.tolerance, 0.5  # temp_wait 0.1
        )
        yield from lakeshore.loop1.wait_until_settled(timeout=20)  # wait for 200 sec or till temperature stablizes

        for ii in range(acq_rep): 
            
            pos_index = np.mod(ii,samx_num*samz_num)

            yield from bps.mv(
                samplestage.x, samx_list[np.mod(pos_index,samx_num)],
                samplestage.z, samz_list[int(np.floor(pos_index/samx_num))]
            )
            
            acq_name = f'{acq_header}_{sample_name}_{ii:04}'

            print(acq_name)

        #         yield from lambda_test(num_iter=1, acquire_time=0.1, acquire_period=0.11, 
        #                 sample_name=acq_name, num_images=2000, sample_suffix="Lq0", analysis_true_false=True)

