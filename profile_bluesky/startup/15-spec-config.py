logger.info(__file__)

"""converted from SPEC config file using apstools.migration.spec2ophyd"""

#flyz = EpicsMotor('8idiAERO:aero:c0:m1', name='flyz', labels=("motor",))
# line 1: MOT001 =    NONE:2/64   2000  1  2000  200   50  125    0 0x003  StrainN  StrainN
tth = EpicsMotor('8idi:sm1', name='tth', labels=("motor",))

pind1z = EpicsMotor('8idi:m3', name='pind1z', labels=("motor",))
pind2z = EpicsMotor('8idi:m4', name='pind2z', labels=("motor",))
pvFLUX_PIND = EpicsMotor('?????????????', name='pvFLUX_PIND', labels=("motor",))

tth_act = EpicsMotor('8idi:m63', name='tth_act', labels=("motor",))
bstop = EpicsMotor('8idi:m27', name='bstop', labels=("motor",))
alpha = EpicsMotor('8idi:sm2', name='alpha', labels=("motor",))
tthAPD = EpicsMotor('8idi:sm3', name='tthAPD', labels=("motor",))
foceye = EpicsMotor('8idi:m37', name='foceye', labels=("motor",))

# What is si6?
#si6vgap = EpicsMotor('8idi:Slit6Vsize', name='si6vgap', labels=("motor",))
#si6vcen = EpicsMotor('8idi:Slit6Vcenter', name='si6vcen', labels=("motor",))
#si6hgap = EpicsMotor('8idi:Slit6Hsize', name='si6hgap', labels=("motor",))
#si6hcen = EpicsMotor('8idi:Slit6Hcenter', name='si6hcen', labels=("motor",))
# Why is this ti4 different from the others?
