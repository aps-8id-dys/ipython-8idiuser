# get all the symbols from the IPython shell
import IPython
globals().update(IPython.get_ipython().user_ns)
logger.info(__file__)


print("Don't forget to call pre_align() with shutter OPEN before you run RE(align_x())")

def align_x(pos_start=-3,
            pos_stop=-3,
            num_pts=61):  
    yield from sb() 
    yield from bp.rel_scan([pind4,lakeshore],samplestage.x,pos_start,pos_stop,num_pts) 
    yield from bb()
                                                                                                                                                     

def align_z(pos_start=-2,
            pos_stop=-2,
            num_pts=41):  
    yield from sb() 
    yield from bp.rel_scan([pind4,lakeshore],samplestage.z,pos_start,pos_stop,num_pts) 
    yield from bb() 
