
from base import Cluster

class Arcus(Cluster):
    name = "ARCUS"
    hostname ="arcus-gpu.oerc.ox.ac.uk"
    username = "jdomanski"
    path = "/data/sbcb-membr/jdomanski"
    status_command = "squeue -u jdomanski"
    status_all_command = "squeue -u jdomanski"
    script = """#!/bin/bash
#SBATCH --job-name=%s
#SBATCH --time=%s
#SBATCH --partition=k20
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
    def parse_qsub(self, result):
        assert "Submitted batch job " in result.output
        return int(result.output.replace("Submitted batch job ", ""))

        
    def get_status(self, shell, job):
        if not job.cluster_id: return None
        cmd = "%s -j %d" % (self.status_command, job.cluster_id)
        try:
            result = shell.run(cmd.split())
        except spur.RunProcessError,e:
            assert "slurm_load_jobs error: Invalid job id specified" in e.stderr_output
            job.status = "C"
            return "C"
        result = result.output.split("\n")
        st = "C"
        if(len(result) == 3):
          jobid, partition, name, user, st, time, nodes, nodelist = result[1].split()
          job.status = st
        return str(st)   
      
    def do_submit(self, shell, remote_workdir,  **kwargs):
        result = shell.run(["sbatch","%s/submit.sh" % remote_workdir], cwd=remote_workdir)  
        return result
    def submit(self, shell, job):        
        result = self.do_submit(shell, job.remote_workdir)
        #"Submitted batch job 2639"
        assert("Submitted batch job" in result.output)
        cluster_id = int(result.output.split()[-1])
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job
        
    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        if status == "R" or status == "PD": # slurm status codes: Running and Pending
          result = shell.run(["scancel", str(job.cluster_id)])
          if result.output:
            return False 
        return True