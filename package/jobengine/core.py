from jobengine.clusters import Emerald, Jade


import configuration
import spur
import uuid
import os, glob
import shutil
#shell = spur.SshShell(hostname="localhost", username="bob", password="password1")

from paramiko import SSHClient
from scp import SCPClient, SCPException

# SQAlchemy-related
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
Base = declarative_base()

class Job(Base):
     __tablename__ = 'jobs'

     id = Column(Integer, primary_key=True)
     name = Column(String)
     uuid = Column(String)
     workdir = Column(String)
     remote_workdir = Column(String)
     local_workdir = Column(String)
     #local_dir = Column(String)
     cluster_name = Column(String)
     cluster_id = Column(Integer)
     nodes = Column(Integer)
     status = Column(String)

     def __init__(self, name, uuid, workdir, local_workdir, remote_workdir, cluster_name, cluster_id, nodes=1):
         self.name = name
         self.uuid = uuid
         self.workdir = workdir
         self.remote_workdir = remote_workdir
         self.cluster_name = cluster_name
         self.cluster_id = cluster_id
         self.status = "U"
         self.local_workdir = local_workdir
         self.current_chemtime = 0.0
         self.target_chemtime = 0.01
         self.nodes = nodes
         

     def __repr__(self):
        return "<Job '%s Cluster: %s'>\n\tId: %d Cluster Id: %d Status: %s UUID: %s\n\tWorkdir: %s\n\tRemote workdir: %s" % (self.name, self.cluster_name, 
                                                                                                                  self.id if self.id else 0,
                                                                                                                  self.cluster_id if self.cluster_id else 0 ,
                                                                                                                  self.status,
                                                                                                                  self.uuid, self.workdir, self.remote_workdir,)

def connect(host):
    
    kwargs = {"password":host.password} if hasattr(host, "password") else {"private_key_file":configuration.private_key_file}
    
    shell = spur.SshShell(
        hostname=host.hostname,
        username=host.username,
        **kwargs
    )
    
    return shell
def stat(host, jobid=None):
    pass
    
def cancel(host):
    pass

from gromacs.fileformats import MDP
from MDAnalysis import Universe
from collections import Counter
import numpy as np
def test_workdir(job):
    from os.path import expanduser
    home = expanduser("~")
    workdir = "{}/.lockers/{}".format(home,job.uuid)
    return test_workdir_contents(os.path.join(workdir, "grompp.mdp"),
                                 os.path.join(workdir, "conf.gro"),
                                 os.path.join(workdir, "traj.xtc"),)


def test_workdir_contents(mdp_file="grompp.mdp", conf_file="conf.gro", traj_file="workdir/traj.xtc"):
    mdp = MDP(mdp_file)
   
    if not   isinstance(mdp["nsteps"],int):
        nsteps = mdp["nsteps"].split()[0]
    else:
        nsteps = mdp["nsteps"]
    target_time = int(nsteps) * mdp["dt"]  # target chemical time in ps
    if not os.path.exists(traj_file): return None, None
    u = Universe(conf_file, traj_file)
    times = [f.time for f in u.trajectory]
    
    # Check if there are no double frames
    c = Counter(times)
    c.most_common(3)
    assert(c.most_common(1)[0][1]  == 1)
    
    # Check if no frames are missing
    desired_times = list(np.arange(0.0, max(times)+mdp["dt"]*mdp["nstxtcout"], mdp["dt"]*mdp["nstxtcout"]))
    assert(len(times) == len(desired_times))
    
    return max(times), target_time

def submit(tpr, cluster):
    assert os.path.isfile(tpr)
    if not os.path.exists(configuration.lockers): os.mkdir(configuration.lockers)
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    shutil.copy(tpr, workdir)
    #open("%s/submit.sh" % workdir,"w").write(cluster.script)
    open("%s/submit.sh" % workdir,"w").write(cluster.get_script(job_name, "%s/.lockers/%s" % (cluster.path, id0))) 
    
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(cluster.hostname, username=cluster.username)
    scp = SCPClient(ssh.get_transport())
    scp.put(workdir, "%s/.lockers/" % (cluster.path), recursive=True)
    
    shell = cluster.connect()
    
    with shell:
        remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
        result = shell.run(["qsub","%s/.lockers/%s/submit.sh" % (cluster.path, id0)], cwd=remote_workdir)
        cluster_id = cluster.parse_qsub(result)
        j = Job("test", id0, workdir, remote_workdir, cluster.name, cluster_id)
    return j

def get_job_from_workdir(session, workdir):
    uuid0 = os.path.basename(os.path.realpath(workdir))
    jobs = [job for job in session.query(Job).order_by(Job.id) if job.uuid == uuid0]
    assert(len(jobs) == 1)
    job = jobs[0]    
    return job

def _copy(pattern, workdir):
	for f in glob.glob(pattern):
		if os.path.exists(f):
			shutil.copy(f, workdir)

def create(tpr, cluster, shell, job_name="workdir", duration="24:00:00", nodes=1, processes=16, script=None):
    assert os.path.isfile(tpr)
    assert os.path.splitext(tpr)[1] == ".tpr"
    if not os.path.exists(configuration.lockers): os.mkdir(configuration.lockers)
    
    # Create workdir, copy files overthere
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    local_dir = os.path.dirname(tpr) # FIXME this should be stored
    shutil.copy(tpr, workdir)
    
    _copy("topol*.tpr", workdir)
    _copy("plumed.dat*", workdir)
    _copy("HILLS*", workdir)
    _copy("*.mdp", workdir)
    _copy("*.pdb", workdir)
    _copy("*.gro", workdir)

    import distutils.core
    
    # Rob's umbrella sampling code
    def copy_to_locker(local_dir, dirname):
        dir = os.path.join(local_dir, dirname)
        if os.path.exists(dir):
            os.mkdir("{}/{}".format(workdir, dirname)) 
            distutils.dir_util.copy_tree(dir, "{}/{}".format(workdir, dirname))
    
    
    copy_to_locker(local_dir, "tpr")
    copy_to_locker(local_dir, "tprs")
    copy_to_locker(local_dir, "qij")
    copy_to_locker(local_dir, "qvt")
    copy_to_locker(local_dir, "mdp")
    
    print nodes, processes, id0
    
    # Use a cluster-specific submit.sh script or not
    if not script:
        open("%s/submit.sh" % workdir,"w").write(cluster.get_script(job_name, "%s/.lockers/%s" % (cluster.path, id0), duration, nodes, processes))
    else: shutil.copy(script, "{}/submit.sh".format(workdir))

    # Setup SSH client to copy files over via scp
    scp = SCPClient(shell.get_transport(), socket_timeout = 600)

    try:
        scp.put(workdir, "%s/.lockers/" % (cluster.path), recursive=True)
    except SCPException, e:
        print "SCPException",e
        shutil.rmtree(workdir)
        os.remove("workdir")
        return None
    
    remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
    print remote_workdir
    out, err = cluster.do_submit(shell, remote_workdir, nodes=nodes, duration=duration)
    print out, err
    cluster_id = cluster.parse_qsub(out)
    j = Job(job_name, id0, workdir, local_dir, remote_workdir, cluster.name, cluster_id, nodes)

    return j        
        
