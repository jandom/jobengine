import spur
from xml.dom import minidom
# paramiko
from paramiko import SSHClient
from scp import SCPClient
from sympy.utilities.runtests import subprocess

def get_cluster(name):
    return clusters[name]

class Job(object):
    
    def __init__(self):
        jobid = None
        status = None
        name = None
        path = None
        stdout = None
        stderr = None

class Cluster(object):
    def __repr__(self):
        return "<Cluster>"
    
    
    def connect(self):
        
        kwargs = {"password":self.password} if hasattr(self, "password") else {"private_key_file":"/home/jandom/.ssh/id_dsa"}
        
        shell = spur.SshShell(
            hostname=self.hostname,
            username=self.username,
            **kwargs
        )
        
        return shell
    def delete(self, shell, cluster_id):
        pass
    cancel = delete
    
class Jade(Cluster):
    name = "JADE"
    hostname ="jade.oerc.ox.ac.uk"
    username = "jdomanski"
    path = "/data/sbcb-membr/jdomanski"
    status_command = "qstat -x"
    script = """#PBS -V
#PBS -N %s
#PBS -l walltime=48:00:00
#PBS -l nodes=1:ppn=6 
#PBS -m bea

module load gromacs/4.6__single
cd $PBS_O_WORKDIR
export MPI_NPROCS=$(wc -l $PBS_NODEFILE | awk '{print $1}')
export OMP_NUM_THREADS=3

if [ -f state.cpt ]; then
  mpirun -np 2 mdrun_mpi  -noconfout -resethway -append -v -cpi
else
  mpirun -np 2 mdrun_mpi  -noconfout -resethway -append -v
fi
"""
    script2 = """#PBS -V
#PBS -N %s
#PBS -l walltime=00:10:00
#PBS -l nodes=1:ppn=1
#PBS -m bea

module load gromacs/4.6__single
cd $PBS_O_WORKDIR
export MPI_NPROCS=$(wc -l $PBS_NODEFILE | awk '{print $1}')
export OMP_NUM_THREADS=3

touch output.txt

if [ -f output.txt ]; then
    date >> output.txt  
else 
    echo "Blah jade" > output.txt
fi

sleep 10
    """
    def parse_qsub(self, result):
        assert len(result.output.split(".")) == 6
        return int(result.output.split(".")[0])

    def pull(self, shell, job):
        """
        Pull the data from remote workdir into the local workdir using the
        scp command.
        """
        cmd = "rsync -v --progress %s@%s:%s/* %s/  --include='*.xtc' --include='*.log' --exclude='*.*' " \
                             % (self.username, self.hostname, job.remote_workdir,  job.workdir)  
        print cmd
        return subprocess.call(cmd, shell=True)
        
          
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
      
    def submit(self, shell, job):
        result = shell.run(["qsub","%s/submit.sh" % job.remote_workdir], cwd=job.remote_workdir)
        cluster_id = self.parse_qsub(result)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job
        
    def delete(self, shell, cluster_id):
        result = shell.run(["qdel", str(cluster_id)])
        if result.output:
            return False
        return True
        
class Emerald(Cluster):
    name = "EMERALD"
    hostname="emerald.einfrastructuresouth.ac.uk"
    username="eisox118"
    path = "/home/oxford/eisox118/"
    #password="password1"
    status_command= "qstat -l emerald".split()
    script = emerald_script = """#!/bin/bash
#BSUB -o %J.log
#BSUB -e %J.err
#BSUB -W 00:05:00
#BSUB -n 1
#BSUB -x

module add libfftw/gnu/3.3.2_mpi
module add gromacs/4.6_mpi

echo "Blah emerald" > output.txt

export MPI_NPROCS=2
    """
    
    def parse_qsub(self, result):
        ids = result.output.split()[1][1:-1], result.output.split()[8][1:-1]
        ids = map(int, ids)
        assert ids[0] == ids[1]
        return ids[0]


    def job_from_string(self,   lines):
        lines = lines.split("\n")
        jobid = int(lines[0].split(";")[1].split(" = ")[1])
        status = lines[1].split()[1]
        name = lines[0].split(";")[0].split(" = ")
        path = lines[6].split(": ")[1]
        stdout = lines[-2].split(" = ")[1]
        stderr = lines[-1].split(" = ")[1]
        j = Job()
        j.jobid = jobid
        j.status = status
        j.name = name
        j.path = path
        j.stdout = stdout
        j.stderr = stderr
        return j

    
    def get_status(self, shell, cluster_id):
        result = shell.run(self.status_command)
        jobs = result.output.split("\n\n")
        jobs = [job_from_string(j) for j in jobs[1:-1]]
        return jobs 
      

clusters = {"jade": Jade, "emerald": Emerald}
      