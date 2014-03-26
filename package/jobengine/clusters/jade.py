import spur
from base import Cluster
import paramiko
from scp import SCPClient
import jobengine.configuration
from xml.dom import minidom
    
class Jade(Cluster):
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

    def parse_qsub(self, result):
        assert len(result.output.split(".")) == 6
        return int(result.output.split(".")[0])
        
    def get_status(self, shell, job):
        if not job.cluster_id: return None
        cmd = self.status_command
        cmd += (" " + str(job.cluster_id))
        try:
            result = shell.run(cmd.split())
        except(spur.RunProcessError):
            job.status = "C"
            return "C"
            
        xmldoc = minidom.parseString(result.output)
        state = xmldoc.getElementsByTagName("job_state")
        if not state: 
          job.status = "C"
          return None
        status = state[0].lastChild.data
        job.status = status
        return str(status) # possible values are "Q"ueued, "R"unning and  "C"omplete

    def do_submit(self, shell, remote_workdir, **kwargs):
        result = shell.run(["qsub","%s/submit.sh" % remote_workdir], cwd=remote_workdir)  
        return result
    
    def submit(self, shell, job, **kwargs):        
        result = self.do_submit(shell, job.remote_workdir)
        cluster_id = self.parse_qsub(result)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job
        
    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        if status == "R":
          result = shell.run(["qdel", str(job.cluster_id)])
          if result.output:
            return False 
        return True
