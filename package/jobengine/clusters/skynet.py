
from pbscluster import PBSCluster

class Skynet(PBSCluster):
    name = "SKYNET"
    hostname ="skynet.oerc.ox.ac.uk"
    script = """#PBS -V
#PBS -N %s
#PBS -l walltime=%s
#PBS -l nodes=1:ppn=4

module purge
module load gromacs/4.6__single
cd $PBS_O_WORKDIR
export MPI_NPROCS=$(wc -l $PBS_NODEFILE | awk '{print $1}')
export OMP_NUM_THREADS=2

if [ -f state.cpt ]; then
  mpirun -np 1 mdrun_mpi  -noconfout -resethway -append -v -cpi -maxh 24
else
  mpirun -np 1 mdrun_mpi  -noconfout -resethway -append -v -maxh 24
fi
"""
