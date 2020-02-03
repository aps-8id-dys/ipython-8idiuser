#!/bin/env python

"""
support for APS data management

USAGE:

This is a companion program to be run when SPEC is run 
for data acquisition.  It may be started before or
after SPEC is started but must be running before triggering
the APS data management workflow.

1. `spec_DM_support.py &`
2. run SPEC

In SPEC, check that helper is running by watching `workflow_ticker`
(`epics_get("8idi:Reg171")`) for 1 second or so.  Should increment ~10/s.
Sample checkup code for SPEC::

    def helper_checkup `{
        v0 = epics_get("8idi:Reg171")
        sleep 1
        dv = epics_get("8idi:Reg171") - v0
        # my SPEC syntax here is sketchy
        if abs(dv) > 8: print("helper is running")
        else:  print("helper is NOT running")
    }`

Trigger the workflow (write HDF5 file and call unix commands) from SPEC:

1. write all the metadata registers
2. write the qmap file name & path (the old way for now)
3. epics_put("8idi:StrReg12", "SPEC")
4. epics_put("8idi:Reg172", submit_xpcs_job)  # 1:analysis, 0:transfer
5. epics_put("8idi:Reg170", 1)  # start
6. while epics_get("8idi:Reg170") == 0: sleep 0.1
7. epics_put("8idi:StrReg12", "")

note about the qmap file:   Lambda_qmap.h5
this file is in:

    /home/8-id-i/partitionMapLibrary/2019-3/

which will work out with the default basename and the hackulated cycle.
"""

import datetime
import epics
import logging
import os
import pyRestTable
import stdlogpj     # pip install stdlogpj
import time

from . import APS_DM_8IDI

BYTE = 1
kB = 1024 * BYTE
MB = 1024*kB

logger = stdlogpj.standard_logging_setup(
    "main", "workflow_helper",
    maxBytes=1*MB, backupCount=9)


class MyPV(object):
    """
    wrapper so we can read waveform strings as strings
    """
    def __init__(self, pv, string=False):
        self.string = string
        self.pv = epics.PV(pv)
        self.description = epics.PV(pv + ".DESC")
        self.data_type = {
            True: "text", 
            False: "number"
            }[pv.find(":StrReg") > 0]
        p = pv.find("Reg")
        n = int(pv[p+3:])
        self.id_str = "%s_%03d" % (self.data_type, n)
    
    def __repr__(self):
        args = '"%s"' % self.pv.pvname
        if self.string:
            args += ", string=True"
        return 'MyPV(%s)' % args

    @property
    def value(self):
        return self.pv.get(as_string=self.string)

    def put(self, value, wait=False, timeout=30):
        if "8idi:Reg171" == self.pv.pvname:     # ticker increment
            response = self.pv.put(value)

        else:
            logger.debug(f'caput("{self.pv.pvname}", {value})')
            try:
                response = self.pv.put(value, wait=wait, timeout=timeout)
            except Exception as exc:
                print(exc)
        
            # implement the wait for ourselves
            t0 = time.time()
            t_end = t0 + 0.05
            while (wait 
                    and 
                    time.time() < t_end 
                    and 
                    self.pv.get(as_string=self.string) != value
                    ):
                time.sleep(0.0002)
        
            msg = (f'value now: {self.pv.get(as_string=self.string)}'
                   f"   in {time.time()-t0:.4f}s")
            logger.debug(msg)
        return response


class DMDBase(object):

    @property
    def pv_attributes(self):
        items = self.__dir__()
        attrs = []
        for k in items:
            if k.startswith("_") or k in ('pv_attributes', 'getTable'):
                continue
            obj = getattr(self, k)
            if isinstance(obj, MyPV):
                attrs.append(k)
        return attrs

    def getTable(self):
        tbl = pyRestTable.Table()
        tbl.labels = "type name PV description value".split()

        def sorter(key):
            obj = getattr(self, key)
            return obj.id_str

        for k in sorted(self.pv_attributes, key=sorter):
            obj = getattr(self, k)
            tbl.addRow(
                [
                    obj.data_type,
                    k,
                    obj.pv.pvname,
                    obj.description.get(),
                    obj.get(),
                ]
            )
        return tbl


class DataManagementMetadata(DMDBase):
    """
    signals for the APS Data Management service
    """
    angle = MyPV("8idi:Reg19")
    ARun_number = MyPV("8idi:Reg173")
    attenuation = MyPV("8idi:Reg110")
    beam_center_x = MyPV("8idi:Reg11")
    beam_center_y = MyPV("8idi:Reg12")
    beam_size_H = MyPV("8idi:Reg151")
    beam_size_V = MyPV("8idi:Reg152")
    burst_mode_state = MyPV("8idi:Reg124")
    ccdxspec = MyPV("8idi:Reg17")
    ccdzspec = MyPV("8idi:Reg18")
    cols = MyPV("8idi:Reg105")
    compression = MyPV("8idi:Reg8")
    dark_begin = MyPV("8idi:Reg111")
    dark_end = MyPV("8idi:Reg112")
    data_begin = MyPV("8idi:Reg113")
    data_end = MyPV("8idi:Reg114")
    datafilename = MyPV("8idi:StrReg5", string=True)
    data_folder = MyPV("8idi:StrReg4", string=True)
    data_subfolder = MyPV("8idi:StrReg10", string=True)
    detector_distance = MyPV("8idi:Reg5")
    detNum = MyPV("8idi:Reg2")
    exposure_period = MyPV("8idi:Reg116")
    exposure_time = MyPV("8idi:Reg115")
    first_usable_burst = MyPV("8idi:Reg126")
    geometry_num = MyPV("8idi:Reg3")
    hdf_metadata_version = MyPV("8idi:Reg1")
    I0mon = MyPV("8idi:Reg123")
    kinetics_state = MyPV("8idi:Reg107")
    kinetics_top = MyPV("8idi:Reg109")
    kinetics_window_size = MyPV("8idi:Reg108")
    last_usable_burst = MyPV("8idi:Reg127")
    number_of_bursts = MyPV("8idi:Reg125")
    ## pid1 = MyPV("8idi:pid1.VAL")
    pid1_set = MyPV("8idi:Reg167")
    pid2_set = MyPV("8idi:Reg168")
    qmap_file = MyPV("8idi:StrReg13", string=True)
    roi_x1 = MyPV("8idi:Reg101")
    roi_x2 = MyPV("8idi:Reg102")
    roi_y1 = MyPV("8idi:Reg103")
    roi_y2 = MyPV("8idi:Reg104")
    root_folder = MyPV("8idi:StrReg2", string=True)
    rows = MyPV("8idi:Reg106")
    sample_pitch = MyPV("8idi:Reg164")
    sample_roll = MyPV("8idi:Reg165")
    sample_yaw = MyPV("8idi:Reg166")
    scan_id = MyPV("8idi:Reg169")
    source_begin_beam_intensity_incident = MyPV("8idi:Reg9")
    source_begin_beam_intensity_transmitted = MyPV("8idi:Reg10")
    source_begin_current = MyPV("8idi:Reg121")
    source_begin_datetime = MyPV("8idi:StrReg6", string=True)
    source_begin_energy = MyPV("8idi:Reg153")
    source_end_current = MyPV("8idi:Reg122")
    source_end_datetime = MyPV("8idi:StrReg7", string=True)
    specfile = MyPV("8idi:StrReg1", string=True)
    specscan_dark_number = MyPV("8idi:Reg117")
    specscan_data_number = MyPV("8idi:Reg118")
    stage_x = MyPV("8idi:Reg119")
    stage_z = MyPV("8idi:Reg120")
    stage_zero_x = MyPV("8idi:Reg13")
    stage_zero_z = MyPV("8idi:Reg14")

    temperature_A = MyPV("8idi:Reg154")
    temperature_B = MyPV("8idi:Reg155")
    temperature_A_set = MyPV("8idi:Reg156")
    temperature_B_set = MyPV("8idi:Reg157")

    translation_table_x = MyPV("8idi:Reg161")
    translation_table_y = MyPV("8idi:Reg162")
    translation_table_z = MyPV("8idi:Reg163")

    translation_x = MyPV("8idi:Reg158")
    translation_y = MyPV("8idi:Reg159")
    translation_z = MyPV("8idi:Reg160")

    uid = MyPV("8idi:StrReg11", string=True)
    user_data_folder = MyPV("8idi:StrReg3", string=True)

    transfer = MyPV("8idi:StrReg15", string=True)
    analysis = MyPV("8idi:StrReg16", string=True)
    workflow_caller = MyPV("8idi:StrReg12", string=True)
    workflow_ticker = MyPV("8idi:Reg171")
    workflow_start = MyPV("8idi:Reg170")
    workflow_submit_xpcs_job = MyPV("8idi:Reg172")
    workflow_uuid = MyPV("8idi:StrReg14", string=True)  # TODO: need to bubble up from workflow thread, somehow

    xpcs_qmap_file = MyPV("8idi:StrReg13", string=True)

    xspec = MyPV("8idi:Reg15")
    zspec = MyPV("8idi:Reg16")


def aps_cycle():
    """Hackulate the name of the current APS run cycle"""
    dt = datetime.datetime.now()
    return f"{dt.year}-{int((dt.month-0.1)/4) + 1}"


class WorkflowHelper:

    def __init__(self):
        logger.debug("WorkflowHelper() constructor")
        # connect metadata register PVs
        self.registers = DataManagementMetadata()
        # get detector information and software that calls the workflow
        self.workflow = APS_DM_8IDI.DM_Workflow(
            self.registers, 
            aps_cycle(), 
            self.registers.xpcs_qmap_file.get(),
            transfer=self.registers.transfer.get(),
            analysis=self.registers.analysis.get(),
            )

        # local attributes to control the polling loop
        self.increment_modulo = 10000   # 0 <= ticker < increment_modulo
        self.increment_interval = 0.1 # seconds
        self.loop_sleep = self.increment_interval/10 # seconds
    
    def incrementTicker(self):
        """increment the ticker to show process is working"""
        n = max(int(self.registers.workflow_ticker.get()), 0)
        self.registers.workflow_ticker.put((n + 1) % self.increment_modulo)

    def runPollingLoop(self):
        """
        watch for signal ('workflow_start') to start data management workflow

        * Increment 'workflow_ticker' at 10 Hz (see self.increment_interval)
        * Ensure 0 <= 'workflow_ticker' < self.increment_modulo
        * when workflow_start!=0 and workflow_caller="spec",
          - run the workflow starter
          - set workflow_start back to 0
          - caller should set workflow_caller back to "" until next time
        """
        logger.info("runPollingLoop() starting")
        t_next_increment = time.time()
        work_in_progress = False

        while True:
            t_now = time.time()
            if t_now >= t_next_increment:
                t_next_increment = t_now + self.increment_interval
                self.incrementTicker()

            if (self.registers.workflow_start.get() != 0
                and 
                self.registers.workflow_caller.get().lower() == "spec"
                and
                not work_in_progress
            ):
                work_in_progress = True
                logger.debug("workflow handling triggered")
                self.workflow.set_xpcs_qmap_file(
                    self.registers.xpcs_qmap_file.get())    # in case this changed
                
                self.workflow.transfer = self.registers.transfer.get()
                self.workflow.analysis = self.registers.analysis.get()
                
                logger.info(f"calling start_workflow(analysis={self.registers.workflow_submit_xpcs_job.get()})")
                t0 = time.time()
                self.workflow.start_workflow(
                    analysis=self.registers.workflow_submit_xpcs_job.get())
                dt = time.time() - t0
                logger.info(f"after starting data management workflow ({dt:.3f}s)")
                logger.info(f"workflow file: {self.workflow.hdf_workflow_file}")
                calls = 0
                while self.registers.workflow_start.get() != 0:
                    self.registers.workflow_start.put(0, wait=True, timeout=0.1)
                    calls += 1
                    if (calls % 10) == 0:
                        logger.warning("retrying caput(trigger PV, 0) {calls} times")
                if calls > 1:
                    logger.warning(f"RETRY: put trigger PV value took {calls} tries")
                logger.debug(f"reset trigger: {self.registers.workflow_start.get()} (should be '0')")
                work_in_progress = False

            time.sleep(self.loop_sleep)


def main():
    logger.debug("starting")
    helper = WorkflowHelper()
    helper.runPollingLoop()


if __name__ == "__main__":
    main()
