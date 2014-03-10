
from base import Cluster

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
