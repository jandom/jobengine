import spur
from base import Cluster
import paramiko
from scp import SCPClient
import jobengine.configuration
from xml.dom import minidom
from arcus import Arcus
    
class Jade(Arcus):
    name = "JADE"
    script = """#!/bin/bash
#SBATCH --job-name=%s
#SBATCH --time=%s
#SBATCH --partition=k10
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=1

set -e

if [ -f state.cpt ]; then
  mpirun -np 1 mdrun_mpi -ntomp 6 -append -v -cpi  -maxh 24 # -noconfout -resethway
else
  mpirun -np 1 mdrun_mpi -ntomp 6 -append -v -maxh 24 #  -noconfout -resethway 
fi
"""