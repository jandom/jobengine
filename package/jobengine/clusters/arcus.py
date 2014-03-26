
from base import Cluster
import spur
class Arcus(Cluster):
    name = "ARCUS-GPU"
    hostname ="arcus-gpu.oerc.ox.ac.uk"
    proxy = "clathrin"
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
        assert(len(result)==1)
        result = result[0]
        assert "Submitted batch job " in result
        return int(result.replace("Submitted batch job ", ""))

        
    def get_status(self, shell, job):
        if not job.cluster_id: return None
        cmd = "%s -j %d" % (self.status_command, job.cluster_id)
        try:
            (stdin, stdout, stderr) = shell.exec_command(cmd)
        except spur.RunProcessError,e:
            assert "slurm_load_jobs error: Invalid job id specified" in e.stderr_output
            job.status = "C"
            return "C"
        result = stdout.readlines()
        st = "C"
        if(len(result) == 2):
            jobid, partition, name, user, st, time, nodes, nodelist = result[1].split()
            job.status = st
        return str(st)   
      
    def do_submit(self, shell, remote_workdir,  **kwargs):
        (stdin, stdout, stderr) = shell.exec_command("cd {}; sbatch {}/submit.sh".format(remote_workdir, remote_workdir))  
        return stdout.readlines()
        
    def submit(self, shell, job):        
        result = self.do_submit(shell, job.remote_workdir)
        #"Submitted batch job 2639"
        assert(len(result) == 1)
        result = result[0]
        assert("Submitted batch job" in result)
        
        cluster_id = int(result.split()[-1])
        job.cluster_id = cluster_id
        print cluster_id
        job.status = self.get_status(shell, job)
        print job.status
        return job
        
    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        if status == "R" or status == "PD": # slurm status codes: Running and Pending
          (stdin, stdout, stderr) = shell.exec_command("scancel {}".format(str(job.cluster_id)))
          if stdout.readlines():
            return False 
        return True
