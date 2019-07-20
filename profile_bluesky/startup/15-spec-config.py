logger.info(__file__)

"""converted from SPEC config file using apstools.migration.spec2ophyd"""

flyz = EpicsMotor('8idiAERO:aero:c0:m1', name='flyz')
# line 1: MOT001 =    NONE:2/64   2000  1  2000  200   50  125    0 0x003  StrainN  StrainN
ti3y = EpicsMotor('8idi:m16', name='ti3y')
si6b = EpicsMotor('8idi:m41', name='si6b')
si6t = EpicsMotor('8idi:m42', name='si6t')
si5x = EpicsMotor('8idi:m55', name='si5x')
si5z = EpicsMotor('8idi:m56', name='si5z')
si6B = EpicsMotor('8idi:m43', name='si6B')
si6T = EpicsMotor('8idi:m44', name='si6T')
tth = EpicsMotor('8idi:m129', name='tth') # misc_par_1 = sm1
sa1vgap = EpicsMotor('8ida:m29', name='sa1vgap') # misc_par_1 = Slit1Vsize
sa1vcen = EpicsMotor('8ida:m30', name='sa1vcen') # misc_par_1 = Slit1Vcenter
sa1hgap = EpicsMotor('8ida:m31', name='sa1hgap') # misc_par_1 = Slit1Hsize
sa1hcen = EpicsMotor('8ida:m32', name='sa1hcen') # misc_par_1 = Slit1Hcenter
ta1_x = EpicsMotor('8ida:m33', name='ta1_x') # misc_par_1 = TA1:x
ta1_z = EpicsMotor('8ida:m34', name='ta1_z') # misc_par_1 = TA1:y
ta2_x = EpicsMotor('8ida:m35', name='ta2_x') # misc_par_1 = TA2:x
ta2_z = EpicsMotor('8ida:m36', name='ta2_z') # misc_par_1 = TA2:y
ta2fine = EpicsMotor('8ida:m37', name='ta2fine') # misc_par_1 = sm9
diamx = EpicsMotor('8idd:m1', name='diamx')
diamz = EpicsMotor('8idd:m2', name='diamz')
ti2_x = EpicsMotor('8idi:m101', name='ti2_x') # misc_par_1 = TI2:x
ti2_z = EpicsMotor('8idi:m102', name='ti2_z') # misc_par_1 = TI2:y
ti3_x = EpicsMotor('8idi:m134', name='ti3_x') # misc_par_1 = TI3:x
ti3_z = EpicsMotor('8idi:m135', name='ti3_z') # misc_par_1 = TI3:y
ti1_x = EpicsMotor('8idi:m130', name='ti1_x') # misc_par_1 = TI1:x
ti1_z = EpicsMotor('8idi:m131', name='ti1_z') # misc_par_1 = TI1:y
si1vgap = EpicsMotor('8idi:m103', name='si1vgap') # misc_par_1 = Slit1Vsize
si1vcen = EpicsMotor('8idi:m104', name='si1vcen') # misc_par_1 = Slit1Vcenter
si1hgap = EpicsMotor('8idi:m105', name='si1hgap') # misc_par_1 = Slit1Hsize
si1hcen = EpicsMotor('8idi:m106', name='si1hcen') # misc_par_1 = Slit1Hcenter
pind1z = EpicsMotor('8idi:m3', name='pind1z')
shuttz = EpicsMotor('8idi:m2', name='shuttz')
bewinx = EpicsMotor('8idi:m17', name='bewinx')
bewinz = EpicsMotor('8idi:m11', name='bewinz')
si1x = EpicsMotor('8idi:m18', name='si1x')
pind2z = EpicsMotor('8idi:m4', name='pind2z')
si3hgap = EpicsMotor('8idi:m109', name='si3hgap') # misc_par_1 = Slit3Hsize
si3hcen = EpicsMotor('8idi:m110', name='si3hcen') # misc_par_1 = Slit3Hcenter
si3vcen = EpicsMotor('8idi:m108', name='si3vcen') # misc_par_1 = Slit3Vcenter
si3vgap = EpicsMotor('8idi:m107', name='si3vgap') # misc_par_1 = Slit3Vsize
si4vgap = EpicsMotor('8idi:m113', name='si4vgap') # misc_par_1 = Slit4Vsize
si4vcen = EpicsMotor('8idi:m114', name='si4vcen') # misc_par_1 = Slit4Vcenter
si4hgap = EpicsMotor('8idi:m115', name='si4hgap') # misc_par_1 = Slit4Hsize
si4hcen = EpicsMotor('8idi:m116', name='si4hcen') # misc_par_1 = Slit4Hcenter
samx = EpicsMotor('8idi:m54', name='samx')
samy = EpicsMotor('8idi:m49', name='samy')
samz = EpicsMotor('8idi:m50', name='samz')
samth = EpicsMotor('8idi:m51', name='samth')
sampit = EpicsMotor('8idi:m52', name='sampit')
samchi = EpicsMotor('8idi:m53', name='samchi')
tth_act = EpicsMotor('8idi:m63', name='tth_act')
bstop = EpicsMotor('8idi:m27', name='bstop')
si2vgap = EpicsMotor('8idi:m123', name='si2vgap') # misc_par_1 = Slit2Vsize
si2vcen = EpicsMotor('8idi:m124', name='si2vcen') # misc_par_1 = Slit2Vcenter
si2hgap = EpicsMotor('8idi:m125', name='si2hgap') # misc_par_1 = Slit2Hsize
si2hcen = EpicsMotor('8idi:m126', name='si2hcen') # misc_par_1 = Slit2Hcenter
ti4_x = EpicsMotor('8idi:m127', name='ti4_x') # misc_par_1 = TI4:x
ti4_z = EpicsMotor('8idi:m128', name='ti4_z') # misc_par_1 = TI4:y
shuttx = EpicsMotor('8idi:m1', name='shuttx')
monoE = EpicsMotor('8idimono:m10', name='monoE') # misc_par_1 = sm2
monoth = EpicsMotor('8idimono:m9', name='monoth') # misc_par_1 = sm1
piezo = EpicsMotor('8idimono:m4', name='piezo')
monopic = EpicsMotor('8idimono:m1', name='monopic')
ccdz = EpicsMotor('8idi:m91', name='ccdz')
alpha = EpicsMotor('8idi:m132', name='alpha') # misc_par_1 = sm2
ti4zu = EpicsMotor('8idi:m30', name='ti4zu')
ti4zdo = EpicsMotor('8idi:m31', name='ti4zdo')
ti4zdi = EpicsMotor('8idi:m32', name='ti4zdi')
ti4xu = EpicsMotor('8idi:m28', name='ti4xu')
ti4xd = EpicsMotor('8idi:m29', name='ti4xd')
tthAPD = EpicsMotor('8idi:m133', name='tthAPD') # misc_par_1 = sm3
ccdx = EpicsMotor('8idi:m90', name='ccdx')
fccdx = EpicsMotor('8idi:m25', name='fccdx')
fccdz = EpicsMotor('8idi:m83', name='fccdz')
foceye = EpicsMotor('8idi:m37', name='foceye')
crlz = EpicsMotor('8idi:m62', name='crlz')
crlpit = EpicsMotor('8idi:m67', name='crlpit')
crlx = EpicsMotor('8idi:m65', name='crlx')
crlyaw = EpicsMotor('8idi:m66', name='crlyaw')
# line 80: MOT080 =    NONE:2/68   2000  1  2000  200   50  125    0 0x003     crly  crly
sa1zu = EpicsMotor('8ida:m11', name='sa1zu')
sa1xu = EpicsMotor('8ida:m14', name='sa1xu')
sa1zd = EpicsMotor('8ida:m15', name='sa1zd')
sa1xd = EpicsMotor('8ida:m16', name='sa1xd')
piezox = EpicsMotor('8idi:m69', name='piezox')
piezoz = EpicsMotor('8idi:m70', name='piezoz')
si6vgap = EpicsMotor('8idi:m136', name='si6vgap') # misc_par_1 = Slit6Vsize
si6vcen = EpicsMotor('8idi:m137', name='si6vcen') # misc_par_1 = Slit6Vcenter
si6hgap = EpicsMotor('8idi:m138', name='si6hgap') # misc_par_1 = Slit6Hsize
si6hcen = EpicsMotor('8idi:m139', name='si6hcen') # misc_par_1 = Slit6Hcenter
si5hgap = EpicsMotor('8idi:m140', name='si5hgap') # misc_par_1 = Slit5Hsize
si5hcen = EpicsMotor('8idi:m141', name='si5hcen') # misc_par_1 = Slit5Hcenter
si5vgap = EpicsMotor('8idi:m142', name='si5vgap') # misc_par_1 = Slit5Vsize
si5vcen = EpicsMotor('8idi:m143', name='si5vcen') # misc_par_1 = Slit5Vcenter
sipvgap = EpicsMotor('8idi:m144', name='sipvgap') # misc_par_1 = SlitpinkVsize
sipvcen = EpicsMotor('8idi:m145', name='sipvcen') # misc_par_1 = SlitpinkVcenter
siphgap = EpicsMotor('8idi:m146', name='siphgap') # misc_par_1 = SlitpinkHsize
siphcen = EpicsMotor('8idi:m147', name='siphcen') # misc_par_1 = SlitpinkHcenter
dsbstpx = EpicsMotor('8idisoft:m1', name='dsbstpx')
dsbstpz = EpicsMotor('8idisoft:m2', name='dsbstpz')
dsccdx = EpicsMotor('8idi:m81', name='dsccdx')
si2t = EpicsMotor('8idi:m46', name='si2t')
si2b = EpicsMotor('8idi:m45', name='si2b')
si2i = EpicsMotor('8idi:m47', name='si2i')
si2o = EpicsMotor('8idi:m48', name='si2o')
dsccdz = EpicsMotor('8idi:m68', name='dsccdz')
# Macro Motor: SpecMotor(mne='si2vg', config_line='107', name='si2vg', macro_prefix='Slit2SoftV') # read_mode = 0
nano = EpicsMotor('8idimono:m5', name='nano') # read_mode = 0
scaler1 = ScalerCH('8idi:scaler1', name='scaler1')
# counter: sec = SpecCounter(mne='sec', config_line='0', name='Seconds', unit='0', chan='0', pvname=8idi:scaler1.S1)
# counter: pind1 = SpecCounter(mne='pind1', config_line='1', name='pind1', unit='0', chan='1', pvname=8idi:scaler1.S2)
# counter: I0Mon = SpecCounter(mne='I0Mon', config_line='2', name='I0Mon', unit='0', chan='7', pvname=8idi:scaler1.S8)
# counter: pind2 = SpecCounter(mne='pind2', config_line='3', name='pind2', unit='0', chan='2', pvname=8idi:scaler1.S3)
# counter: pind3 = SpecCounter(mne='pind3', config_line='4', name='pind3', unit='0', chan='3', pvname=8idi:scaler1.S4)
# counter: pind4 = SpecCounter(mne='pind4', config_line='5', name='pind4', unit='0', chan='4', pvname=8idi:scaler1.S5)
# counter: pdbs = SpecCounter(mne='pdbs', config_line='6', name='pdbs', unit='0', chan='5', pvname=8idi:scaler1.S6)
# counter: I_APS = SpecCounter(mne='I_APS', config_line='7', name='I_APS', unit='0', chan='6', pvname=8idi:scaler1.S7)
# line 8: CNT008 =     NONE  2  0      1 0x000     ccdc  ccdc
Atten1 = EpicsSignal('8idi:userTran1.P', name='Atten1')
Atten2 = EpicsSignal('8idi:userTran3.P', name='Atten2')
T_A = EpicsSignal('8idi:LS336:TC4:IN1', name='T_A')
T_SET = EpicsSignal('8idi:LS336:TC4:OUT1:SP', name='T_SET')
# counter: APD = SpecCounter(mne='APD', config_line='13', name='APD', unit='0', chan='8', pvname=8idi:scaler1.S9)
