logger.info(__file__)

"""local, custom Device definitions"""


class CompoundRefractiveLensDevice(Device):
    x = Component(EpicsMotor, '8idi:m65', labels=["motor", "crl", "optics"])
    # y = Component(EpicsMotor, '8idi:m68', labels=["motor", "crl", "optics"])
    z = Component(EpicsMotor, '8idi:m62', labels=["motor", "crl", "optics"])
    pitch = Component(EpicsMotor, '8idi:m67', labels=["motor", "crl", "optics"])
    yaw = Component(EpicsMotor, '8idi:m66', labels=["motor", "crl", "optics"])


class MonochromatorDevice(Device):
    energy = Component(EpicsMotor, '8idimono:sm2', labels=["motor", "mono", "optics"])
    theta = Component(EpicsMotor, '8idimono:sm1', labels=["motor", "mono", "optics"])
    piezo = Component(EpicsMotor, '8idimono:m4', labels=["motor", "mono", "optics"])
    pico = Component(EpicsMotor, '8idimono:m1', labels=["motor", "mono", "optics"])
    nano = Component(EpicsMotor, '8idimono:m5', labels=["motor", "mono", "optics"])
    x = Component(EpicsMotor, '8idi:TI1:x', labels=["motor", "mono", "optics", "table"])
    z = Component(EpicsMotor, '8idi:TI1:y', labels=["motor", "mono", "optics", "table"])


class WBslitDevice(Device):  
    """
    White Beam Slit in 8-ID-A
    """
    vgap = Component(EpicsMotor, '8ida:Slit1Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8ida:Slit1Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8ida:Slit1Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8ida:Slit1Hcenter', labels=["motor", "slit"])
    zu = Component(EpicsMotor, '8ida:m11', labels=["motor", "slit"])    
    xu = Component(EpicsMotor, '8ida:m14', labels=["motor", "slit"])    
    zd = Component(EpicsMotor, '8ida:m15', labels=["motor", "slit"])
    xd = Component(EpicsMotor, '8ida:m16', labels=["motor", "slit"])

class SlitI1Device(Device):  
    """
    Slit1 in 8-ID-I
    """
    x = Component(EpicsMotor, '8idi:m18', labels=["motor", "slit"])
    vgap = Component(EpicsMotor, '8idi:Slit1Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit1Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit1Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit1Hcenter', labels=["motor", "slit"])
    
class SlitI2Device(Device):  
    """
    Slit2 in 8-ID-I
    """
    vgap = Component(EpicsMotor, '8idi:Slit2Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit2Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit2Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit2Hcenter', labels=["motor", "slit"])    
    
class SlitI3Device(Device):  
    """
    Slit3 in 8-ID-I
    """
    vgap = Component(EpicsMotor, '8idi:Slit3Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit3Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit3Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit3Hcenter', labels=["motor", "slit"])    
    
class SlitI4Device(Device):  
    """
    Slit4 in 8-ID-I
    """
    vgap = Component(EpicsMotor, '8idi:Slit4Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit4Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit4Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit4Hcenter', labels=["motor", "slit"])    
    
class SlitI5Device(Device):  
    """
    Slit5 in 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:m55', labels=["motor", "slit"])
    z = Component(EpicsMotor, '8idi:m56', labels=["motor", "slit"])
    vgap = Component(EpicsMotor, '8idi:Slit5Vsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:Slit5Vcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:Slit5Hsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:Slit5Hcenter', labels=["motor", "slit"])

class SlitIpinkDevice(Device):  
    """
    Slitpink in 8-ID-I
    """    
    vgap = Component(EpicsMotor, '8idi:SlitpinkVsize', labels=["motor", "slit"])
    vcen = Component(EpicsMotor, '8idi:SlitpinkVcenter', labels=["motor", "slit"])
    hgap = Component(EpicsMotor, '8idi:SlitpinkHsize', labels=["motor", "slit"])
    hcen = Component(EpicsMotor, '8idi:SlitpinkHcenter', labels=["motor", "slit"])
    
    
class FOEpinholeDevice(Device):  
    """
    Optics Table 1 in 8-ID-A which holds the 270 um pin hole for heat load reduction
    """    
    x = Component(EpicsMotor, '8ida:TA1:x', labels=["motor", "table"]) 
    z = Component(EpicsMotor, '8ida:TA1:y', labels=["motor", "table"])
  

class FOEmirrorDevice(Device):  
    """
    Optics Table 2 in 8-ID-A which holds the First optical element Mirror
    """    
    x = Component(EpicsMotor, '8ida:TA2:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8ida:TA2:y', labels=["motor", "table"])
    fine = Component(EpicsMotor, '8ida:sm9', labels=["motor", "table"])


class BeamSplittingMonochromatorDevice(Device):  
    """
    I/E Beam-splitting Silicon monochromator in 8-ID-D
    """    
    x = Component(EpicsMotor, '8idd:m1', labels=["motor", "optics"])
    z = Component(EpicsMotor, '8idd:m2', labels=["motor", "optics"])


class TableOptics(Device):  
    """
    Optics Table 2 in 8-ID-I which holds optics and slits
    """    
    x = Component(EpicsMotor, '8idi:TI2:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8idi:TI2:y', labels=["motor", "table"])
   
 
class FlightPathTable(Device):  
    """
    Optics Table 1 in 8-ID-A which holds the 270 um pin hole for heat load reduction
    """    
    x = Component(EpicsMotor, '8ida:TA1:x', labels=["motor", "table"]) 
    z = Component(EpicsMotor, '8ida:TA1:y', labels=["motor", "table"])
  

class FOEmirrorDevice(Device):  
    """
    Optics Table 2 in 8-ID-A which holds the First optical element Mirror
    """    
    x = Component(EpicsMotor, '8ida:TA2:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8ida:TA2:y', labels=["motor", "table"])
    fine = Component(EpicsMotor, '8ida:sm9', labels=["motor", "table"])


class BeamSplittingMonochromatorDevice(Device):  
    """
    I/E Beam-splitting Silicon monochromator in 8-ID-D
    """    
    x = Component(EpicsMotor, '8idd:m1', labels=["motor", "optics"])
    z = Component(EpicsMotor, '8idd:m2', labels=["motor", "optics"])


class TableOptics(Device):  
    """
    Optics Table 2 in 8-ID-I which holds optics and slits
    """    
    x = Component(EpicsMotor, '8idi:TI2:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8idi:TI2:y', labels=["motor", "table"])
    
    
class TI3(Device):  
    """
    Optics Table 3 in 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:TI3:x', labels=["motor", "table"])
    y = Component(EpicsMotor, '8idi:m16', labels=["motor", "table"])  # ? Why is ti3 the only one that has a y stage?
    z = Component(EpicsMotor, '8idi:TI3:y', labels=["motor", "table"])
    

class TI4(Device):  
    """
    Optics Table 4 in 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:TI4:x', labels=["motor", "table"])
    z = Component(EpicsMotor, '8idi:TI4:y', labels=["motor", "table"])
    
    
class BeWindow(Device):  
    """
    Beryllium Window 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:m17', labels=["motor", "optics"])
    z = Component(EpicsMotor, '8idi:m11', labels=["motor", "optics"])

        
class ShutterStage(Device):  
    """
    Shutter Stage at 8-ID-I
    """    
    x = Component(EpicsMotor, '8idi:m1', labels=["motor", "shutter"])
    z = Component(EpicsMotor, '8idi:m2', labels=["motor", "shutter"])
    
            
class DetStageUpstream(Device):  
    """
    Upstream detector stage at 4 m (the old 'ccdx' and 'ccdz')
    """    
    x = Component(EpicsMotor, '8idi:m90', labels=["motor", "det"])
    z = Component(EpicsMotor, '8idi:m91', labels=["motor", "det"])
  

class DetStageDownstream(Device):  
    """
    Downstream detector stage at 8 m (the old 'fccdx' and 'fccdz')
    """    
    x = Component(EpicsMotor, '8idi:m25', labels=["motor", "det"])
    z = Component(EpicsMotor, '8idi:m83', labels=["motor", "det"])

    
#class Piezo(Device):  
#    """
#    Piezo stage at the sample?
#    """    
#    x = Component(EpicsMotor, '8idi:m69', labels=["motor", "sample"])
#    z = Component(EpicsMotor, '8idi:m70', labels=["motor", "sample"])

    
class SampleStageUpstream(Device):
    """
    Sample stages 
    """

    samx = EpicsMotor('8idi:m54', name='samx', labels=("motor",))
    samy = EpicsMotor('8idi:m49', name='samy', labels=("motor",))
    samz = EpicsMotor('8idi:m50', name='samz', labels=("motor",))
    samth = EpicsMotor('8idi:m51', name='samth', labels=("motor",))
    sampit = EpicsMotor('8idi:m52', name='sampit', labels=("motor",))
    samchi = EpicsMotor('8idi:m53', name='samchi', labels=("motor",))
    tablex = Component(EpicsMotor, '8idi:TI3:x', labels=["motor", "table"])
    tabley = Component(EpicsMotor, '8idi:TI3:z', labels=["motor", "table"])  # ? Why is ti3 the only one that has a y stage?
    tablez = Component(EpicsMotor, '8idi:TI3:y', labels=["motor", "table"])
