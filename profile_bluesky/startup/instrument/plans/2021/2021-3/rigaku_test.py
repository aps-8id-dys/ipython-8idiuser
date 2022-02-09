

from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt
from bluesky import plan_stubs as bps


def Rigaku_Fast(rigaku500k, num_repeats=5):

    yield from bps.mv(rigaku500k.cam1.acquire_time, 20e-6)    
    yield from bps.mv(rigaku500k.cam1.image_mode, 5)   
    yield from bps.mv(rigaku500k.cam1.trigger_mode, 4)   
    yield from bps.mv(rigaku500k.cam1.num_images, 100000)   
    yield from bps.mv(rigaku500k.cam1.corrections, "Enabled")       
    yield from bps.mv(rigaku500k.cam1.data_type, "UInt32") 
    yield from bps.mv(rigaku500k.cam1.file_path, '2021-3/bluesky202112/') 
    rigaku500k.cam1.acquire.put_complete = False  
    
    # unix('rm -rf /home/8ididata/RigakuEpics/test*')

    for ival in range(1, num_repeats):
    
        _filename= "ZDT{:02d}_{:06d}.bin".format(1,ival)

        while rigaku500k.cam1.det_state.get(as_string=True) != "Idle":
            yield from bps.sleep(0.1)

        print(f"Start Rigaku Acquire: {_filename}")
    
        while rigaku500k.cam1.det_state.get(as_string=True) == "Idle":
            yield from bps.sleep(0.1)
#            print('Do sleep')
            yield from bps.mv(rigaku500k.cam1.file_name, _filename)  
#            print('Set file name')   
            yield from bps.mv(rigaku500k.cam1.acquire, 1) 
#            print('Set acquire')                 
