

import os
import sys
path = os.path.join(
    os.environ["HOME"], 
    ".ipython-bluesky",
    "profile_bluesky",
    "startup")
sys.path.append(path)
from instrument.collection import *


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit

%run -m lambda_testing


acq_header = 'A100'
acq_rep = 100
sample_name = 'Silica-D100'


samx_min = -1
samx_max = 1
samx_num = 21

samz_min = -0.5
samz_max = 0.5
samz_num = 11

Temp_list = [26, 28, 29, 30]

from instrument.devices import samplestage

print(samplestage.x.position)
print(samplestage.z.position)
lakeshore.loop1.target.get()


acq_name = f'{scan_header}_{sample_name}_{scans_rep:04}'

samx_list = np.linspace(samx_min, samx_max, num=samx_num)
samz_list = np.linspace(samz_min, samz_max, num=samz_num)

def my_way():
    for kk in range(len(Temp_list)):   
        yield from bps.mv(
            lakeshore.loop1.target Temp_list[kk],  # te $Temp
            lakeshore.loop1.tolerance, 0.1  # temp_wait 0.1
        )
        yield from lakeshore.loop1.wait_until_settled(timeout=20)  # wait for 200 sec or till temperature stablizes
        
        for ii in range(scans_rep):    
            
            yield from bps.mv(
                samplestage.x, samx_list[np.mod(ii,samx_num)]
                samplestage.z, samz_list[int(np.floor(ii/samx_num))]
            )
            
            print(acq_name)
            
    #         yield from lambda_test(num_iter=1, acquire_time=0.1, acquire_period=0.11, 
    #                 sample_name=acq_name, num_images=2000, sample_suffix="Lq0", analysis_true_false=True)


RE(my_way())
