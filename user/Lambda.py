# get all the symbols from the IPython shell
import IPython
import os
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)
#from bluesky import plan_stubs as bps
#from bluesky import plan_preprocesors as bpp


"""
define cam params such as acquire time, period, num images, camera mode
define file plugin immout params such as file path,file name, num_images, file_number, capture

configure scaler channels for monitoring some scalers and devices such as temperature

trigger area detector while monitoring the above params

"""

def Lambda_Acquire(det, acquire_time=0.1, acquire_period=0.11,num_images=100,file_name="A001"):
    path = "/home/8-id-i/2019-2/jemian_201908"
    file_path = os.path.join(path,file_name)
    if not file_path.endswith(os.path.sep):
        file_path += os.path.sep
    
    # Ask the device to configure itself for this work.
    # no need to yield here, method does not have "yield from " calls
    det.staging_setup_DM(file_path, file_name,
            num_images, acquire_time, acquire_period)

    scaler1.stage_sigs["count_mode"] = "AutoCount"
    scaler1.stage_sigs["auto_count_time"] = max(0.1,acquire_period)
   
    scaler1.select_channels(None) 
    monitored_things = [
        #scaler1.channels.chan01,
        #scaler1.channels.chan02,
        #scaler1.channels.chan03,
        Atten1,
        Atten2,
        T_A,
        T_SET,
    ]
    """
        #Timebase,
        pind1,
        pind2,
        pind3,
        pind4,
        pdbs,
        I_APS,
        I0Mon,
        APD,
        cstar_l,
        cstar_h,
        oxygen,
        scaler1_time,
    """

    @bpp.stage_decorator([scaler1])
    @bpp.monitor_during_decorator(monitored_things)
    def inner():
        md = {
            "file_name": file_name,
            "file_path": file_path
        }
        yield from bps.mv(scaler1.count,"Count")
        yield from bp.count([det], md=md)

    return (yield from inner())

