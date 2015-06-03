

from biowulf2 import Biowulf2
import spur
class Biowulf2IB(Biowulf2):
    name = "BIOWULF2IB"
    
    def do_submit(self, shell, remote_workdir,  **kwargs):
        (stdin, stdout, stderr) = shell.exec_command("cd {}; {} --partition=ibfdr --job-name=gmx  --nodes={} --exclusive --ntasks-per-node=16  --time={} {}/submit.sh".format(remote_workdir, self.submit_command, kwargs.get('nodes', 1), kwargs.get('duration', '24:00:00'), remote_workdir))  
        return stdout.readlines(), stderr.readlines()
