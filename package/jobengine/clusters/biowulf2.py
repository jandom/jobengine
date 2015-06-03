

from slurmcluster import SlurmCluster
import spur
class Biowulf2(SlurmCluster):
    name = "BIOWULF2"
    proxy = None
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"

    status_command = "squeue -u domanskij"
    status_all_command = "squeue -u domanskij"
    script = """#!/bin/bash
#SBATCH --job-name=%s
#SBATCH --time=%s
#SBATCH --partition=ibfdr
#SBATCH --ntasks=16
#SBATCH --exclusive
#SBATCH --ntasks-per-core=1

set -e

if [ -f state.cpt ]; then
  mpirun -np 1 mdrun_mpi -ntomp 6 -append -v -cpi  -maxh 24 # -noconfout -resethway
else
  mpirun -np 1 mdrun_mpi -ntomp 6 -append -v -maxh 24 #  -noconfout -resethway 
fi
"""
    def parse_qsub(self, result):
        print "result", result
        assert(len(result)==1)
        result = result[0]
        return int(result)

        
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
        (stdin, stdout, stderr) = shell.exec_command("cd {}; sbatch --partition=norm --job-name=gmx  --nodes={} --exclusive --ntasks-per-node=16  --time={} {}/submit.sh".format(remote_workdir, kwargs.get('nodes', 1), kwargs.get('duration', '24:00:00'), remote_workdir))  
        return stdout.readlines(), stderr.readlines()
        
    def submit(self, shell, job, **kwargs):        
	kwargs["nodes"] = job.nodes 
        out, err = self.do_submit(shell, job.remote_workdir, **kwargs)
        
        cluster_id = int(out[0])
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
