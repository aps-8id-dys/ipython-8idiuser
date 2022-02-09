

### Modularized code that handles **only** Rigaku ZDT acquisition 
### Does not communicate to DM
### Completely independent from other detectors or even other modes on the same detector

from ophyd import Device
from ophyd import EpicsSignal
from ophyd import Component as Cpt
from bluesky import plan_stubs as bps


class Info_User(Device): 
    det_directory = Component(Signal, value=None)
    scan_directory = Component(Signal, value=None)

    def select_path(self, user_index):
        yield from bps.mv(self.det_directory, f'/home/8idiuser/{aps.aps_cycle.get()}/{user_index}')
        yield from bps.mv(self.scan_directory, f'/home/beams10/8IDIUSER/bluesky_data/{aps.aps_cycle.get()}')

class Info_Detector(Device): 

    # def __init__(self):
    #     self.detector_name = None
    #     self.qmapname = None
    #     self.filename = None
    #     self.trigger_mode = None
    #     self.acquisition_mode = None
    #     self.acquisition_time = None
    #     self.acquisition_period = None

    detector_name = Component(Signal, value=None)
    filename = Component(Signal, value=None)
    trigger_mode = Component(Signal, value=None)
    acquisition_mode = Component(Signal, value=None)

    qmapname = Component(Signal, value=None)
    acquisition_time = Component(Signal, value=None)
    acquisition_period = Component(Signal, value=None)

    def select_qmap(self, qmap_name: str):
        """
        set qmap
        """
        yield from bps.mv(self.qmapname, f'/home/8-id-i/{aps.aps_cycle.get()}/{qmap_name}')
        # self.qmapname.put(f'/home/8-id-i/{aps.aps_cycle.get()}/{qmap_name}')

    def select_det_mode(self, detector_name, trigger_mode, acquisition_mode):
        yield from bps.mv(self.detector_name, detector_name)
        yield from bps.mv(self.trigger_mode, trigger_mode)
        yield from bps.mv(self.acquisition_mode, acquisition_mode)
        
        if detector_name == 'rigaku500k' and trigger_mode == 0 and acquisition_mode == 'fast':
            # self.stage_sigs = {}
            # self.stage_sigs["cam.acquire"] = 0
            # self.stage_sigs["cam.acquire_time"] = 20e-6
            self.stage_sigs["cam.image_mode"] = "2 Bit, Zero-Deadtime"
            # self.stage_sigs["cam.trigger_mode"] = "ZDT Fixed Time"
            # self.stage_sigs["cam.num_images"] = 100_000  # "_" is a visual separator
            # self.stage_sigs["cam.corrections"] = "Enabled"
            # self.stage_sigs["cam.data_type"] = "UInt32"

            # ophyd.areadetector.cam.CamBase
            # Attributes: acquire, acquire_time, image_mode, trigger_mode, num_images, corrections, data_type

            rigaku500k.cam.acquire.put(0)
            rigaku500k.cam.acquire_time.put(30e-6)
            rigaku500k.cam.image_mode.put("2 Bit, Zero-Deadtime")
            rigaku500k.cam.trigger_mode.put("ZDT Fixed Time")
            rigaku500k.cam.num_images.put(100_000)
            rigaku500k.cam.corrections.put("Enabled")
            rigaku500k.cam.data_type.put("UInt32")


# class Info_Sample: 
#     def __init__(self):
#         self.sample_name = None
#         self.id_char = None
#         self.samx_center = None
#         self.samx_scan_halfwidth = None
#         self.samx_num_points = None
#         self.samz_center = None
#         self.samz_scan_halfwidth = None
#         self.samz_num_points = None
#         self.qnw_position = None
#         self.qnw_name = None
        
#     def select(self, sample_index):
#         """Load sample information from json file"""
#         # read the json file
#         # find the sample_index
#         config = json_dict[sample_index]
#         self.sample_name = ["sample_name"]
#         self.id_char = ["samp_id_char"]



class Run_Object(Device):
    info_user = Component(Info_User)
    info_detector = Component(Info_Detector)

run_object = Run_Object(name="run_object")

def detector_acq(run_object, num_repeat=1):
    
    def acq_1():
        return (yield from bps.repeat(partial(bps.trigger, rigaku500k, wait=True), num_repeat))

    return (yield from acq_1())









    
