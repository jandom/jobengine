import spur
from base import Cluster
import paramiko
from scp import SCPClient
import jobengine.configuration
from xml.dom import minidom
    
class PBSCluster(Cluster):
    name = "JADE"
    proxy = "clathrin"
    hostname ="jade.oerc.ox.ac.uk"
    username = "jdomanski"
    path = "/data/sbcb-membr/jdomanski"
    status_command = "qstat -x"
    status_all_command = "qstat -u jdomanski"
    script = """#PBS -V
#PBS -N %s
#PBS -l walltime=%s
#PBS -l nodes=1:ppn=3
#PBS -m bea

module purge
module load gromacs/4.6__single
cd $PBS_O_WORKDIR
export MPI_NPROCS=$(wc -l $PBS_NODEFILE | awk '{print $1}')
export OMP_NUM_THREADS=3

if [ -f state.cpt ]; then
  mpirun -np 1 mdrun_mpi  -resethway -append -v -cpi -maxh 24
else
  mpirun -np 1 mdrun_mpi  -resethway -append -v -maxh 24
fi
"""

    def parse_qsub(self, stdout):
        lines = stdout.readlines()
        assert(len(lines)==1)
        #print lines
        cluster_id = int(lines[0].split(".")[0])
        return cluster_id  
        
    def get_status(self, shell, job):
        (stdin, stdout, stderr) = shell.exec_command("qstat {}".format(job.cluster_id))
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        if len(stderr) and "Unknown Job Id" in stderr[0]: 
            job.status = "C"
            return "C" 
        #print stdout, stderr
        assert(len(stdout)==3)
        status_code = stdout[-1].split()[-2]
        return str(status_code)

    def do_submit(self, shell, remote_workdir, **kwargs):
        print kwargs.get('nodes', 1)
        (stdin, stdout, stderr) = shell.exec_command("cd {}; qsub submit.sh".format(remote_workdir))
        return stdout    
    
    def submit(self, shell, job, **kwargs):        
        result = self.do_submit(shell, job.remote_workdir)
        cluster_id = self.parse_qsub(result)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job
        
    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        if status == "R":
          cmd = "qdel {}".format(str(job.cluster_id))
          (stdin, stdout, stderr) = shell.exec_command(cmd)
          if stdout:
            return False 
        return True
