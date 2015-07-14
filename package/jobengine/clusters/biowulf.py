
from pbscluster import PBSCluster
from scp import SCPClient
import jobengine.configuration

class Biowulf(PBSCluster):
    """
    Access to biowulf is much more contrived then others - we're using its definition 
    from the ~/.ssh/config which includes a ProxyCommand
    
    spur cannot support ProxyCommand, so lower-level paramiko is used. 
    The standard connect() method is overriden. 
    """
    name = "BIOWULF"
    proxy = None
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    status_all_command= "/usr/local/pbs/bin/qstat -u {}".format(username)

    def parse_qsub(self, lines):
        assert(len(lines)==1)
        cluster_id = int(lines[0].split(".biobos")[0])
        return cluster_id      

    def get_script(self, *args):
        return self.script % (args[0][:15], args[2], args[3]*args[4])
    
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
          print cmd
          (stdin, stdout, stderr) = shell.exec_command(cmd)
          print stdout.readlines(), stderr.readlines()
          if stdout:
            return False 
        return True
    
    def get_status(self, shell, job):
        (stdin, stdout, stderr) = shell.exec_command("/usr/local/pbs/bin/qstat {}.biobos".format(job.cluster_id))
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        if len(stderr) and "Unknown Job Id" in stderr[0]: 
            job.status = "C"
            return "C" 
        assert(len(stdout)==3)
        status_code = stdout[-1].split()[-2]
        return str(status_code)
      
    def do_submit(self, shell, remote_workdir, **kwargs):
        print kwargs.get('nodes', 1)
        (stdin, stdout, stderr) = shell.exec_command("cd {}; /usr/local/pbs/bin/qsub -q lcp -l nodes={},walltime={} submit.sh".format(remote_workdir, kwargs.get('nodes', 1), kwargs.get('duration', '24:00:00')))
        return stdout.readlines(), stderr.readlines()  
    def submit(self, shell, job, **kwargs):
        #result = shell.run(["qsub","-q", "lcp", "-l", "nodes=12","%s/submit.sh" % job.remote_workdir], cwd=job.remote_workdir)
        #(stdin, stdout, stderr) = shell.exec_command("cd {}; /usr/local/pbs/bin/qsub -q lcp -l nodes=10 submit.sh".format(job.remote_workdir))
        kwargs["nodes"] = job.nodes
        
        stdout, stderr = self.do_submit(shell, job.remote_workdir, **kwargs)
	print stdout, stderr
        cluster_id = self.parse_qsub(stdout)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job 
