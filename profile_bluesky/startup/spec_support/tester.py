#!/bin/env python

import os
import sys
import time

sys.path.append("/home/beams/8IDIUSER/.ipython-bluesky/profile_bluesky/startup")

t0 = time.time()
from spec_support import spec_DM_support
connected = f"connected in {time.time()-t0:.3f}s"

print(spec_DM_support.registers.getTable())
print(connected)
print(f"finished in {time.time()-t0:.3f}s")
print(spec_DM_support.workflow.detectors.manufacturerDict)

workflow_file = "/tmp/workflow.h5"
print(f"before writing HDF5: {workflow_file} exists: {os.path.exists(workflow_file)}")
spec_DM_support.workflow.create_hdf5_file(workflow_file)
print(f"after writing HDF5: {workflow_file} exists: {os.path.exists(workflow_file)}")
