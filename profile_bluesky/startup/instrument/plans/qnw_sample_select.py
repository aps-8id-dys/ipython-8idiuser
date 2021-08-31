

__all__ = [
    'select_sample',
    'te_qnw',
    
]

import json
from bluesky import plans as bp
from bluesky import plan_stubs as bps
from instrument.devices import samplestage, qnw_device
from instrument.session_logs import logger
logger.info(__file__)
import os


yield from bps.mv(qnw_env1, 25)


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
    with open(os.path.join(path,file_name), 'r') as f1:
        _ = json.load(f1)
    print(_["qnw_env"])

    if _["qnw_env"] == "qnw_env1":
        yield from bps.mv(qnw_env1.ramprate, ramp_rate)  
        if temp_wait is True:
            yield from bps.mv(qnw_env1.tolerance, tolerance)
            yield from bps.mv(qnw_env1, set_temp)      
        if temp_wait is False:
            yield from bps.abs_set(qnw_env1, set_temp)   
        
    if _["qnw_env"] == "qnw_env2":
        yield from bps.mv(qnw_env2.ramprate, ramp_rate) 
        if temp_wait is True:
            yield from bps.mv(qnw_env2.tolerance, tolerance)
            yield from bps.mv(qnw_env2, set_temp)      
        if temp_wait is False:
            yield from bps.abs_set(qnw_env2, set_temp)  

    if _["qnw_env"] == "qnw_env3":
        yield from bps.mv(qnw_env3.ramprate, ramp_rate) 
        if temp_wait is True:
            yield from bps.mv(qnw_env3.tolerance, tolerance)
            yield from bps.mv(qnw_env3, set_temp)      
        if temp_wait is False:
            yield from bps.abs_set(qnw_env3, set_temp)    

 