

"""
Acquisition of Rigaku Zero-Dead-Time 52 kHz mode
Bypassing EPICS file plugin and save directly as .bin binary format
"""



__all__ = [
    'Rigaku_52kHz',
]



from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt
from bluesky import plan_stubs as bps


def Rigaku_52kHz(rigaku500k, num_repeats=5):
    """
    Modularized code that handles **only** Rigaku ZDT acquisition 
    Does not talk to DM Workflow     
    Completely independent from other detectors or even other modes on the same detector
    """

    yield from bps.mv(rigaku500k.cam1.acquire_time, 20e-6)    
    yield from bps.mv(rigaku500k.cam1.image_mode, 5)   
    yield from bps.mv(rigaku500k.cam1.trigger_mode, 4)   
    yield from bps.mv(rigaku500k.cam1.num_images, 100000)   
    yield from bps.mv(rigaku500k.cam1.corrections, "Enabled")       
    yield from bps.mv(rigaku500k.cam1.data_type, "UInt32")

    # TO-DO: 
    # Read folder name, etc. from Init_User 
    # Read sample name from Init_QNW. For now assume all users will use QNW.
    yield from bps.mv(rigaku500k.cam1.file_path, '2021-3/bluesky202112/')  

    for ival in range(1, num_repeats):
    
        _filename= "ZDT{:02d}_{:06d}.bin".format(1,ival)

        while rigaku500k.cam1.det_state.get(as_string=True) != "Idle":
            yield from bps.sleep(0.1)

        print(f"Start Rigaku Acquire: {_filename}")
    
        while rigaku500k.cam1.det_state.get(as_string=True) == "Idle":
            yield from bps.sleep(0.1)
            yield from bps.mv(rigaku500k.cam1.file_name, _filename)  
            yield from bps.mv(rigaku500k.cam1.acquire, 1) 
             
