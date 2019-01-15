#!/bin/bash
#module load pytorch/v1.0.0-intel ## not in 
export PYTHONPATH=$PYTHONPATH:/global/homes/x/xju/track/gnn/code/python_pkg/install/lib/python3.7/site-packages

/usr/common/software/pytorch/v1.0.0-intel/bin/python -m ipykernel_launcher $@
