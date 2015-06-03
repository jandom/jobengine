
import subprocess
import spur
from jobengine.configuration import config
import paramiko

class Cluster(object):
    name = None
    hostname = None
    username = None
    proxy = None
    path = None
    def __repr__(self):
        return "<Cluster '%s' %s@%s:%s>" % (self.name, self.username, self.hostname, self.path)
    def get_script(self, *args):
        return self.script % (args[0], args[2])
      
    def _rsync(self, verbose):
        verbose=True
        return "/usr/bin/rsync -e '{proxy}' {verbose} {flags}".format(**{"proxy": ("ssh -q {} ssh".format(self.proxy) if self.proxy else "ssh -q"), 
                                                                         "verbose": ('-v  --progress' if verbose else ''),
                                                                         "flags": config.rsync.flags,
                                                                         })
            
    def pull(self, shell, job, verbose=False):
        """
        Pull the data from remote workdir into the local workdir using the
        scp command.
        """
        from os.path import expanduser
        home = expanduser("~")
        cmd = "%s %s@%s:%s/* /%s/.lockers/%s/ " \
                             % (self._rsync(verbose), self.username, self.hostname, job.remote_workdir, home, job.uuid)
        cmd += " --include='*.xtc' --include='*.trr' --include='*.gro' --include='*.mdp' --include='*.sh' --include='*HILLS*' --include='*COLVAR*' --include='*.cpt' --include='*.dat'  --include='*.log' --include='*.ndx' --include='*.edr'  --include='*.qvt' --exclude='*.*' "
        print cmd
        return subprocess.call(cmd, shell=True)    

    def push(self, shell, job, pattern=None, verbose=False):
        """
        Pull the data from remote workdir into the local workdir using the
        scp command.
        """
        #assert(pattern)
        from os.path import expanduser
        home = expanduser("~")
        cmd = "%s ~/.lockers/%s/* %s@%s:~/.lockers/%s  " \
                             % (self._rsync(verbose), job.uuid, self.username, self.hostname, job.uuid)
        #cmd += " --include='*.xtc' --include='*.gro' --include='*HILLS*' --include='*COLVAR*' --include='*.dat'  --include='*.log' --include='*.ndx' --exclude='*.*' "
        if verbose: print(cmd)
        print cmd
        return subprocess.call(cmd, shell=True)    
    
    def delete(self, shell, job):
        cmd = "mv ~/.lockers/{} ~/.trash".format(job.uuid)
        print cmd
        (stdin, stdout, stderr) = shell.exec_command(cmd)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        print stdout, stderr
        return 0

    def cancel(self, shell, cluster_id):
        raise NotImplementedError
        pass

    def connect(self):

        host = config.ssh.lookup(self.name.lower())

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if 'proxycommand' in host:
            proxy = paramiko.ProxyCommand(host['proxycommand'])
            ret = client.connect(host["hostname"], username=host["user"], pkey=config.dsa_key, sock=proxy, timeout=300)
        else:
            ret = client.connect(host["hostname"], username=host["user"], pkey=config.dsa_key, timeout=300)
        return client

    def get_status_all(self, shell):
        raise NotImplementedError
        pass
