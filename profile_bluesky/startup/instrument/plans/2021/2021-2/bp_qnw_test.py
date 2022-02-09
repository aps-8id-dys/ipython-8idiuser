
from bluesky import plans as bp
from bluesky import plan_stubs as bps
from instrument.collection import *
from instrument.devices import aps
from instrument.framework import bec, RE
from instrument.devices import lakeshore, flyscan, adrigaku
from instrument.plans import AD_Acquire, movesample, select_RIGAKU
import json


path = "/home/beams/8IDIUSER/bluesky_data/2021/2021-2"

def select_sample(index=None):
    file_name = 'QNW_sample_definitions.json'
    with open(os.path.join(path,file_name), 'r') as f1:
        _ = json.load(f1)  

    tmp = json.dumps(_[index], indent = 4)
    with open(os.path.join(path,"current_sample.json"), 'w') as f2:
        f2.write(tmp)

    yield from bps.mv(samplestage.qnw_x, _[index]['qnw_position'])  


def te_qnw(set_temp=None, ramp_rate=5, temp_wait=False, tolerance=0.1):  

    file_name = 'current_sample.json'
    with open(os.path.join(path,file_name), 'r') as f:
        _ = json.load(f)
   
    qnw_env = globals()[_["qnw_env"]]   
    yield from bps.mv(qnw_env.ramprate, ramp_rate)    

    if temp_wait is True:
        yield from bps.mv(qnw_env.tolerance, tolerance)
        yield from bps.mv(qnw_env, set_temp)      
    if temp_wait is False:
        yield from bps.abs_set(qnw_env, set_temp)     



    