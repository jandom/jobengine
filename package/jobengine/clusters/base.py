
import subprocess
import spur
import jobengine.configuration
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
        return "/usr/bin/rsync -e '{proxy}' {verbose} -a --compress --timeout=30".format(**{"proxy": ("ssh -q {} ssh".format(self.proxy) if self.proxy else "ssh -q"), 
                                                                                            "verbose": ('-v  --progress' if verbose else '')})
      
    def test_pull(self, shell, remote_file, local_file, verbose=False):
        cmd = "%s %s@%s:%s %s"  \
                             % (self._rsync(verbose), self.username, self.hostname, remote_file, local_file)        
        print cmd
        return subprocess.call(cmd, shell=True)
          
    def test_push(self, shell, local_file, remote_file, verbose=False):
        cmd = "%s %s %s@%s:%s" \
                             % (self._rsync(verbose), local_file, self.username, self.hostname, remote_file, )
        print cmd
        return subprocess.call(cmd, shell=True)
            
    def pull(self, shell, job, verbose=False):
        """
        Pull the data from remote workdir into the local workdir using the
        scp command.
        """
        from os.path import expanduser
	home = expanduser("~")
	cmd = "%s %s@%s:%s/* /%s/.lockers/%s/ " \
                             % (self._rsync(verbose), self.username, self.hostname, job.remote_workdir, home, job.uuid)
        cmd += " --include='*.xtc' --include='*.gro' --include='*HILLS*' --include='*COLVAR*' --include='*.dat'  --include='*.log' --include='*.ndx' --include='*.edr'  --include='*.qvt' --exclude='*.*' "
        print cmd
        return subprocess.call(cmd, shell=True)    

    def push(self, shell, job, pattern=None, verbose=False):
        """
        Pull the data from remote workdir into the local workdir using the
        scp command.
        """
        assert(pattern)
	from os.path import expanduser
	home = expanduser("~")
        cmd = "%s %s/%s %s@%s:%s/.lockers/%s/  " \
                             % (self._rsync(verbose), home, job.uuid, pattern, self.username, self.hostname, job.remote_workdir)
        #cmd += " --include='*.xtc' --include='*.gro' --include='*HILLS*' --include='*COLVAR*' --include='*.dat'  --include='*.log' --include='*.ndx' --exclude='*.*' "
        if verbose: print(cmd)
        print cmd
        return subprocess.call(cmd, shell=True)    
    
    def cancel(self, shell, cluster_id):
        pass
    delete = cancel

    def connect(self):
        dsa_key = paramiko.DSSKey.from_private_key_file(jobengine.configuration.private_key_file)
        conf = paramiko.SSHConfig()
	from os.path import expanduser
	home = expanduser("~")
        conf.parse(open('{}/.ssh/config'.format(home)))
        host = conf.lookup(self.name.lower())

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if 'proxycommand' in host:
            
            proxy = paramiko.ProxyCommand(host['proxycommand'])
            ret = client.connect(host["hostname"], username=host["user"], pkey=dsa_key, sock=proxy, timeout=300)
        else:
            ret = client.connect(host["hostname"], username=host["user"], pkey=dsa_key, timeout=300)
        return client

    def get_status_all(self, shell):
        #print self.status_all_command
        (stdin, stdout, stderr) = shell.exec_command(self.status_all_command)
        stdout = stdout.readlines()
        stderr = stderr.readlines()
        return "".join(stdout)
