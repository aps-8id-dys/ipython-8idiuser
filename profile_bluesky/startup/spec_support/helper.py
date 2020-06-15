#!/bin/env python

"""
runs the workflow_helper daemon

Run this command from the UNIX command line to
start the helper in the background:

    cd /home/beams/8IDIUSER/.ipython-bluesky/profile_bluesky/startup/spec_support
    bash
    source ~/bin/use_bluesky_conda_environment.sh
    helper.py &

It will emit log messages when a workflow is operating.
These messages will be saved in a file:
<pwd>/.logs/.workflow_helper.log
(pwd is the present working directory).
Once this code is found to be reliable, we can 
simplify the startup and running of this helper.
"""

import os
import sys
import time

_path = os.path.dirname(__file__)
sys.path.append(os.path.join(_path, ".."))

from spec_support import spec_DM_support


def test_create_hdf5_file():
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


if __name__ == "__main__":
    # test_create_hdf5_file()
    spec_DM_support.main()
