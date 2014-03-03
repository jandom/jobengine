import spur
from xml.dom import minidom
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import subprocess
import jobengine.configuration

class Job(object):
    
    def __init__(self):
        jobid = None
        status = None
        name = None
        path = None
        stdout = None
        stderr = None


class Cluster(object):
    name = None
    hostname = None
    username = None
    path = None
    def __repr__(self):
        return "<Cluster '%s' %s@%s:%s>" % (self.name, self.username, self.hostname, self.path)
    def get_script(self, *args):
        return self.script % (args[0], args[2])
    def pull(self, shell, job, verbose=False):
        """
        Pull the data from remote workdir into the local workdir using the
        scp command.
        """
        
        # -v --progress
        cmd = "rsync  %s@%s:%s/* %s/  --include='*.xtc' --include='*.gro' --include='*HILLS*' --include='*.log' --include='*.ndx' --exclude='*.*' " \
                             % (self.username, self.hostname, job.remote_workdir,  job.workdir)  
        if verbose: print(cmd)
        return subprocess.call(cmd, shell=True)    
    
    def connect(self):
        
        kwargs = {"password":self.password} if hasattr(self, "password") else {"private_key_file":jobengine.configuration.private_key_file}
        
        shell = spur.SshShell(
            hostname=self.hostname,
            username=self.username,
            **kwargs
        )
        
        return shell
    def cancel(self, shell, cluster_id):
        pass
    delete = cancel

      
    def get_status_all(self, shell):
        result = shell.run(self.status_all_command.split())
        return result.output

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
      
    def do_submit(self, shell, remote_workdir):
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
    
class Jade(Cluster):
    name = "JADE"
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

class Skynet(Jade):
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

class Hal(Jade):
    name = "HAL"
    hostname ="hal.oerc.ox.ac.uk"

class Biowulf(Jade):
    """
    Access to biowulf is much more contrived then others - we're using its definition 
    from the ~/.ssh/config which includes a ProxyCommand
    
    spur cannot support ProxyCommand, so lower-level paramiko is used. 
    The standard connect() method is overriden. 
    """
    name = "BIOWULF"
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    status_command= "qstat -l lcp".split()

    def parse_qsub(self, stdout):
        lines = stdout.readlines()
        assert(len(lines)==1)
        cluster_id = int(lines[0].split(".biobos")[0])
        return cluster_id      

    def get_script(self, *args):
        return self.script % (args[0][:15], args[2], 16*args[3])
    
    def get_scp(self):
        client = self.connect()
        print client
        (stdin, stdout, stderr) = client.exec_command("uname -a")    
        scp = SCPClient(client.get_transport())
        print scp
        return scp

    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        if status == "R":
          cmd = "/usr/local/pbs/bin/qdel {}".format(str(job.cluster_id))
          (stdin, stdout, stderr) = shell.exec_command(cmd)
          if stdout:
            return False 
        return True
    
    def get_status_all(self, shell):
        (stdin, stdout, stderr) = shell.exec_command("/usr/local/pbs/bin/qstat -u {}".format(self.username))
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        return "".join(stdout)
        
    def get_status(self, shell, job):
        (stdin, stdout, stderr) = shell.exec_command("/usr/local/pbs/bin/qstat {}".format(job.cluster_id))
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        if len(stderr) and "Unknown Job Id" in stderr[0]: 
            job.status = "C"
            return "C" 
        assert(len(stdout)==3)
        status_code = stdout[-1].split()[-2]
        return str(status_code)
    
    def connect(self):
        dsa_key = paramiko.DSSKey.from_private_key_file(jobengine.configuration.private_key_file)
        
        conf = paramiko.SSHConfig()
        conf.parse(open('/home/jandom/.ssh/config'))
        host = conf.lookup('biowulf')

        proxy = paramiko.ProxyCommand(host['proxycommand'])
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host["hostname"], username=host["user"], pkey=dsa_key, sock=proxy)

        return client
    def do_submit(self, shell, remote_workdir, **kwargs):
        print kwargs.get('nodes', 1)
        (stdin, stdout, stderr) = shell.exec_command("cd {}; /usr/local/pbs/bin/qsub -q lcp -l nodes={} submit.sh".format(remote_workdir, kwargs.get('nodes', 1)))
        return stdout    
    def submit(self, shell, job, **kwargs):
        #result = shell.run(["qsub","-q", "lcp", "-l", "nodes=12","%s/submit.sh" % job.remote_workdir], cwd=job.remote_workdir)
        #(stdin, stdout, stderr) = shell.exec_command("cd {}; /usr/local/pbs/bin/qsub -q lcp -l nodes=10 submit.sh".format(job.remote_workdir))
        kwargs["nodes"] = job.nodes
        stdout = self.do_submit(shell, job.remote_workdir, **kwargs)
        cluster_id = self.parse_qsub(stdout)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job 
    script = """#!/bin/bash

#PBS -N "%s"

##PBS -l nodes=1:c24,walltime=%s

#source /usr/local/gromacs/bin/GMXRC

module load openmpi/1.6.4/intel/ib
module load gromacs/4.5.5+plumed-ib

mpirun=`which mpirun`
application=`which mdrun_mpi`

cd ${PBS_O_WORKDIR}

np=%d

if [ -f plumed.dat ]; then
  options="-v -plumed -maxh 24"
else
  options="-v -maxh 24"
fi

echo "Running: $mpirun -np $np $application $options"

if [ -f state.cpt ]; then
  $mpirun -machinefile $PBS_NODEFILE -n $np $application $options -cpi
else
  $mpirun -machinefile $PBS_NODEFILE -n $np $application $options
fi
    
"""
        
class Emerald(Cluster):
    name = "EMERALD"
    hostname="emerald.einfrastructuresouth.ac.uk"
    username="eisox118"
    path = "/home/oxford/eisox118/"
    #password="password1"
    status_command= "qstat -l emerald".split()
    status_all_command= "qstat -u eisox118 emerald"
    script = """#BSUB -J {0}
#BSUB -o %J.log
#BSUB -e %J.err
#BSUB -W 24:00
#BSUB -m emerald3g
#BSUB -n 1
#BSUB -x

module add libfftw/gnu/3.3.2_mpi
module add gromacs/4.6_mpi

#cd %s

if [ -f state.cpt ]; then
  mpirun -np 2 mdrun_mpi  -noconfout -resethway -append -v -cpi -maxh 24
else
  mpirun -np 2 mdrun_mpi  -noconfout -resethway -append -v -maxh 24
fi
"""
    
    def parse_qsub(self, result):
        ids = result.output.split()[1][1:-1], result.output.split()[8][1:-1]
        ids = map(int, ids)
        assert ids[0] == ids[1]
        #print "ids=", ids
        return ids[0]

    def get_script(self, job_name, remote_workdir):
	return self.script % (job_name, remote_workdir)

    def job_from_string(self, lines):
        lines = lines.split("\n")	
        jobid = int(lines[0].split(";")[1].split(" = ")[1])
        status = lines[1].split()[1]
        assert status in ["WAITING", "RUNNING"]
        name = lines[0].split(";")[0].split(" = ")
        path = lines[5].split(": ")[1]
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

    def submit(self, shell, job):
        result = shell.run(["bsub" ," < ","%s/submit.sh" % job.remote_workdir], cwd=job.remote_workdir)
        cluster_id = self.parse_qsub(result)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job
    
    def get_status(self, shell, job):
        if not job.cluster_id: return None
        result = shell.run(self.status_command)
        jobs = result.output.split("\n\n")
        jobs = [self.job_from_string(j) for j in jobs[1:-1]]
        #print "cluster_id=", job.cluster_id	
        #for j in jobs: print "job.jobid=",j.jobid
        jobs = [j for j in jobs if j.jobid == job.cluster_id]
        if len(jobs) == 0: return "C"
        assert len(jobs) == 1
        job = jobs[0]
        status = job.status
        assert status in ["WAITING", "RUNNING"]
        if status == "WAITING": return "Q"
        if status == "RUNNING": return "R"


class Clusters(object):
    clusters = {"jade": Jade, "emerald": Emerald, "arcus": Arcus, "hal": Hal, "skynet": Skynet, "biowulf": Biowulf}
    def __init__(self):
        self.__clusters_cache = {}    
    def get_cluster(self, cluster_name):
        cluster_name = cluster_name.lower()
        if self.__clusters_cache.has_key(cluster_name):
            return self.__clusters_cache[cluster_name]
        cluster = self.clusters[cluster_name]
        
        cluster = cluster()
        shell = cluster.connect()
        self.__clusters_cache[cluster_name] = (cluster, shell)
        return cluster, shell
      
