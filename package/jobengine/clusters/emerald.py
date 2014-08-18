
from base import Cluster

class Emerald(Cluster):
    name = "EMERALD"
    hostname="emerald.einfrastructuresouth.ac.uk"
    username="eisox118"
    path = "/home/oxford/eisox118/"
    proxy = "clathrin"
    #password="password1"
    status_command= "qstat -l emerald".split()
    status_all_command= "qstat -u eisox118 emerald"
    script = """#BSUB -J {}
#BSUB -o %J.log
#BSUB -e %J.err
#BSUB -W {}
#BSUB -q emerald-devel
#BSUB -n {}
#BSUB -x

module add libfftw/gnu/3.3.2_mpi
module add gromacs/4.6_mpi

#cd %s

if [ -f state.cpt ]; then
  mpirun -np {} mdrun_mpi  -v -cpi -maxh 24 # -noconfout -resethway -append 
else
  mpirun -np {} mdrun_mpi  -v -maxh 24 # -noconfout -resethway -append 
fi
"""
    
    def parse_qsub(self, stdout):
        ids = stdout.split()[1][1:-1], stdout.split()[8][1:-1]
        ids = map(int, ids)
        assert ids[0] == ids[1]
        #print "ids=", ids
        return ids[0]

    def get_script(self, job_name, remote_workdir, duration, nodes, processes):
        return self.script.format(job_name, duration, nodes, remote_workdir, processes, processes)

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

    def do_submit(self, shell, remote_workdir, nodes, duration):
        (stdin, stdout, stderr)  = shell.exec_command("bsub" ," < ","%s/submit.sh" % remote_workdir)
        print stdin
        print stdout
        print stderr
        print stdout.readlines()
        print stderr.readlines()
        
        return stdout.readlines(), stderr.readlines()

        cluster_id = self.parse_qsub(stdout)
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
