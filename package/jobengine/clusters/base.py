
import subprocess
import spur
import jobengine.configuration

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
        
        cmd = "/usr/bin/rsync   -e 'ssh -q' -va --progress --compress %s@%s:%s/* %s/  --include='*.xtc' --include='*.gro' --include='*HILLS*' --include='*.log' --include='*.ndx' --exclude='*.*' " \
                             % (self.username, self.hostname, job.remote_workdir,  job.workdir)  
        if verbose: print(cmd)
        print cmd
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