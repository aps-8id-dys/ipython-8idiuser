#!/bin/env python

import os
import sys
import time

_path = os.path.dirname(__file__)
sys.path.append(os.path.join(_path, ".."))

from spec_support import spec_DM_support
t0 = time.time()
helper = spec_DM_support.WorkflowHelper()
connected = f"connected in {time.time()-t0:.3f}s"

print(helper.registers.getTable())
print(connected)
print(f"finished in {time.time()-t0:.3f}s")
print(helper.workflow.detectors.manufacturerDict)

workflow_file = "/tmp/workflow.h5"
print(f"before writing HDF5: {workflow_file} exists: {os.path.exists(workflow_file)}")
t0 = time.time()
helper.workflow.create_hdf5_file(workflow_file)
print(f"created HDF5 file in {time.time()-t0:.3f}s")
print(f"after writing HDF5: {workflow_file} exists: {os.path.exists(workflow_file)}")
