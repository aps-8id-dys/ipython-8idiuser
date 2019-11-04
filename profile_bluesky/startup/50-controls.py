logger.info(__file__)

"""local, custom Bluesky plans (scans)"""


# access by subscript or by name (obj[0]= same as obj.insert)
# NOTE: "in" is a Python keyword that cannot be re-used
insert_remove_tuple = namedtuple('insert_remove_tuple', 'insert remove')

class Presets:
    """
    various instrument settings and constants
    """
    pind1z = insert_remove_tuple(1, 0)
    pind2z = insert_remove_tuple(1, 0)
    pvFLUX_PIND = insert_remove_tuple(1, 0)

presets = Presets()

# Bluesky plans to move the diodes in/out

def insert_diodes():
    "insert ALL the diodes"
    yield from bps.mv(
        pind1z, presets.pind1z.insert,
        pind2z, presets.pind2z.insert,
        pvFLUX_PIND, presets.pvFLUX_PIND.insert,
    )

def remove_diodes():
    "remove ALL the diodes"
    yield from bps.mv(
        pind1z, presets.pind1z.remove,
        pind2z, presets.pind2z.remove,
        pvFLUX_PIND, presets.pvFLUX_PIND.remove,
    )

def insert_pind1z():
    yield from bps.mv(pind1z, presets.pind1z.insert)

def remove_pind1z_out():
    yield from bps.mv(pind1z, presets.pind1z.remove)

def insert_pind2z():
    yield from bps.mv(pind2z, presets.pind2z.insert)

def remove_pind2z():
    yield from bps.mv(pind2z, presets.pind2z.remove)

def insert_pvFLUX_PIND():
    yield from bps.mv(pvFLUX_PIND, presets.pvFLUX_PIND.insert)

def remove_pvFLUX_PIND():
    yield from bps.mv(pvFLUX_PIND, presets.pvFLUX_PIND.remove)


# alignment plans

def lineup_and_center(channel, motor, minus, plus, npts, time_s=0.1, _md={}):
    """
    lineup and center a given axis, relative to current position

    PARAMETERS
    
    channel : scaler channel object
        detector to be maximized
    
    axis : motor
        motor to use for alignment
    
    minus : float
        first point of scan at this offset from starting position
    
    plus : float
        last point of scan at this offset from starting position
    
    npts : int
        number of data points in the scan
    
    time_s : float (default: 0.1)
        count time per step

    EXAMPLE:

        RE(lineup_and_center("diode", ta2fine, -30, 30, 30, 1.0))
    """
    old_sigs = scaler.stage_sigs
    scaler.stage_sigs["preset_time"] = time_s
    # yield from bps.mv(scaler.preset_time, time_s)

    scaler.select_channels([channel.name])
    clock.kind = Kind.normal

    md = dict(_md)
    md["purpose"] = "alignment"
    yield from bp.rel_scan([scaler], motor, minus, plus, npts, md=md)

    table = pyRestTable.Table()
    table.labels = ("key", "value")
    table.addRow(("motor", motor.name))
    table.addRow(("detector", channel.name))
    for key in ('com', 'cen', 'max', 'min', 'fwhm', 'nlls'):
        # TODO: if channel.name not in bec.peaks[key] then report that no scan has been done
        table.addRow((key, bec.peaks[key][channel.name]))
    logger.info("alignment scan results:")
    logger.info(str(table))

    # move motor to centroid
    yield from bp.mv(motor, bec.peaks["cen"][channel.name])

    # TODO: check if the position is ok
    # TODO:tweak ta2fine 2 to maximize

    scaler.select_channels(None)
    scaler.stage_sigs = old_sigs


def Rinaldi_group_alignment(_md={}):
    # TODO: this looks like a macro for the "user" folder
    md = dict(_md)

    channel = pind1     # the EpicsSignalRO (scaler channel) object, not the string name
    motor = ta2fine     # the EpicsMotor object, not the string name
    yield from insert_pind1z()

    yield from bp.mv(si1.x, 0.0)
    yield from bp.mvr(diamond.x, -1)     # NOTE: *relative* move here
    yield from bp.mv(
        si1.hcen, 0,
        si1.hgap, 250,
        si1.vgap, 250,
    )

    yield from lineup_and_center(channel, motor, -30, 30, 30, 1.0, md=md)

    yield from flux(pind1, cps)     # FIXME: cps is undefined here!
    ##flux should be 1.0-1.6 E12 ph/sec

    yield from bp.mv(si1.x, 0.2)
    yield from bp.mvr(diamond.x, 1.0)     # NOTE: *relative* move here
    yield from bp.mv(
        si1.hcen, 50,
        si1.hgap, 60,
        si1.vgap, 150,
    )


def flux(pin_diode, photocurrent):
    """
    """
    raise NotImplementedError("Need to write the Bluesky flux() plan")

    """
736.SPEC8IDI> prdef flux

# /home/beams/S8SPEC/spec/macros/sites/spec8IDI/site_f.mac
def flux '{
	if ($# !=2) {
	eprint "Usage: flux pin_diode cps"
	exit
	}
	preamp_setread;
    params = flux_params("$1")
    print_flux_params params "$1"
    #printf("\n %g cps is a current of %g Amps \n",$2,\
     #      ($2/params["CtpV"])*params["Amps_per_Volt"])
    printf("\n %g cps is a current of %g Amps \n",$2,\
           ($2/params["CtpV"])*Amps_per_Volt["$1"])
    printf("\n %8.3g photons per second \n",calc_flux($2,params,"$1"))
  }'

737.SPEC8IDI> prdef preamp_setread

# /home/beams/S8SPEC/spec/macros/sites/spec8IDI/site_f.mac
def preamp_setread '{
  	local amp_scale;
	local strPVUnit, strPVNum, strID;

	for (i = 1; i <= 5; i++) {
    		strPVUnit = "8idi:A" i "sens_unit.VAL";
    		strPVNum = "8idi:A" i "sens_num.VAL";
    		_unit = epics_get(strPVUnit);
		sleep(0.1);
    		_num = epics_get(strPVNum);
		sleep(0.1);
    		if (_unit =="mA/V") amp_scale=1e-3;
    		if (_unit =="uA/V") amp_scale=1e-6;
    		if (_unit =="nA/V") amp_scale=1e-9;
    		if (_unit =="pA/V") amp_scale=1e-12;
		if (i == 1)
			strID = "pind1";
		else if (i == 2)
		 	strID = "pind2";
		else if (i == 3)
			strID = "pind3";
		else if (i == 4)
			strID = "pind4";
		else
			strID = "pdbs";
    		Amps_per_Volt[strID] = (_num)*amp_scale;

       		if (Amps_per_Volt[strID]==0.0) {
       			printf("\nLooks like SPEC is not getting the sensitivity of  %s (Amps/Volt) from EPICS\n",strID); 
       			exit
		}
	}

}'

739.SPEC8IDI> prdef flux_params

# /home/beams/S8SPEC/spec/macros/sites/spec8IDI/site_f.mac
def flux_params(_counter) '{
  local Elength result Mabs N_elec 

  result["Amps_per_Volt"] = Amps_per_Volt[_counter];

	CtpV=1e5
  result["CtpV"] = CtpV

	Length=0.04
  result["fluxLength"] = Length

	Element="Si"
   result["Element"] = Element

  #Ephot=epics_get("ID08us:Energy.VAL")*1000-100
  Ephot=epics_get("8idimono:sm2.RBV")*1000
  result["Ephot"] = Ephot
  Ekev = Ephot/1000;

  if (Element == "Ar") {
	N_elec = Ephot/26.4; 
	Elength =  exp(-2.78262);
	Elength *= exp(.782515*Ekev);
	Elength *= exp(-.0379763*Ekev*Ekev);
	Elength *= exp(1.04293e-3*Ekev*Ekev*Ekev);
	Elength *= exp(-1.14407e-5*Ekev*Ekev*Ekev*Ekev);
	}
  else if ( Element == "N2") {
	N_elec = Ephot/34.8;
	Mabs =  exp(6.17639);
	Mabs *= exp(-6.90647e-1*Ekev);
	Mabs *= exp(2.44039e-2*Ekev*Ekev);
	Mabs *= exp(-.453977e-3*Ekev*Ekev*Ekev);
	Mabs *= exp(0.033084e-4*Ekev*Ekev*Ekev*Ekev);
	Elength = 1.0/(Mabs*1.165e-3);
	}
  else if ( Element == "He") {
	N_elec = Ephot/41.3;
	Elength =  exp(15.4707);
	Elength *= exp(0.972059*Ekev);
	Elength *= exp(-0.0487191*Ekev*Ekev);
	Elength *= exp(0.00134312*Ekev*Ekev*Ekev);
	Elength *= exp(-1.46011e-05*Ekev*Ekev*Ekev*Ekev);
	Elength /=1e4;
	}
  else if (Element == "Si") {
	N_elec = Ephot/3.62;
	Elength = 61e-4*pow((7.65/Ekev),-3);
	Length = 400e-4;
	}
  else {
	printf("This program does not yet calculate %s \n",Element);
	exit
	}
  result["N_elec"] = N_elec
  result["Elength"] = Elength
  result["Abs_frac"] = (1-exp(-Length/Elength));
  return(result)
  }'
    """
    # TODO:
    pass


def bb(*args, **kwargs):
    """
    block beam

    bb -> blockbeam -> blockbeam_Lambda

    # /home/beams/8IDIUSER/batches/2019/Oct2019/Lambda_rubber_both4X.do
    def blockbeam 'blockbeam_Lambda'

    745.SPEC8IDI> prdef blockbeam_Lambda

    # /home/beams/8IDIUSER/local_macros/CCD_macros/xpcs_ad_nofpga_Lambda_AD3p0_EXTTRIG.mac
    def blockbeam_Lambda '
        ##epics_put("8idi:BioEnc2B1.VAL","Down");
        ##epics_put("8idi:BioEnc2B3.VAL","Close");
        epics_put("8idi:Unidig1Bo13","Closed");
    '

    """
    yield from bp.mv(shutter, "close")


def sb(*args, **kwargs):
    """show beam"""
    yield from bp.mv(shutter, "open")


def tw(channel, motor, delta):
    """
    maximize a positioner using a motor and reading a scaler channel

    In SPEC, the `tw` command initiates an interactive session.
    Automate that here, if possible.
    """
    # Usage:  tw mot [mot2 ...] delta [delta2 ...] [count_time]
    raise NotImplementedError("Need to write the Bluesky tw() plan")
