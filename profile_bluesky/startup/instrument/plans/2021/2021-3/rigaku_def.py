
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt
from bluesky import plan_stubs as bps

# merged class
class Rigaku500k_Cam1(Device):  
    # CAM1
    acquire_time = Cpt(EpicsSignal, 'AcquireTime')
    image_mode = Cpt(EpicsSignal, 'ImageMode')
    trigger_mode = Cpt(EpicsSignal, 'TriggerMode')
    num_images = Cpt(EpicsSignal, 'NumImages')
    corrections = Cpt(EpicsSignal, 'Corrections')
    data_type = Cpt(EpicsSignal, 'DataType')
    
    det_state = Cpt(EpicsSignal, 'DetectorState_RBV', string=True) 
    file_name = Cpt(EpicsSignal, 'FileName', string=True) 
    file_path = Cpt(EpicsSignal, 'FilePath', string=True)    
    acquire = Cpt(EpicsSignal, 'Acquire')  
    num_que_arrays = Cpt(EpicsSignal, 'NumQueuedArrays') 

class Rigaku500k_HDF1(Device):
    # HDF1
    auto_inc = Cpt(EpicsSignal, 'AutoIncrement') 
    num_capture = Cpt(EpicsSignal, 'NumCapture')
    file_name = Cpt(EpicsSignal, 'FileName', string=True)
    file_num = Cpt(EpicsSignal, 'FileNumber')
    capture = Cpt(EpicsSignal, 'Capture_RBV')

# object
class Rigaku500k(Device):
    cam1 = Rigaku500k_Cam1('8idRigaku:cam1:', name='cam1')
    hdf1 = Rigaku500k_HDF1('8idRigaku:HDF1:', name='hdf1')


# Creating a custom device 
rigaku500k = Rigaku500k('8idRigaku',name="rigaku500k")
