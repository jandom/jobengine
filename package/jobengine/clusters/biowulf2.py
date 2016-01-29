

from slurmcluster import SlurmCluster

class Biowulf2(SlurmCluster):
    name = "BIOWULF2"
    proxy = None
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    partitions = ["norm", "ibfdr", "niddk"]

    def do_submit(self, shell, job,  **kwargs):
        # get the defaults 
        partition = kwargs.get('partition', job.partition) 
        jobname = kwargs.get('jobname', job.name)
        nodes = kwargs.get('nodes', job.nodes) 
        ntasks = kwargs.get("ntasks_per_node", 16)
        duration = kwargs.get('duration', '24:00:00')

        cmd = "cd {}; {} --partition={} --job-name={}  --nodes={} {} --ntasks-per-node={} --time={} {}/submit.sh".format(
                job.remote_workdir, 
                self.submit_command, 
                partition,
                jobname, 
                nodes,
                "--exclusive", # if kwargs.get('ntasks_per_node', 16) == 16 else "",
                ntasks, 
                duration,
                job.remote_workdir
            )

        print(cmd)
        (stdin, stdout, stderr) = shell.exec_command(cmd)  
        return stdout.readlines(), stderr.readlines()
        
    def submit(self, shell, job, **kwargs):        

        out, err = self.do_submit(shell, job, **kwargs)        
        print out, err
        cluster_id = int(out[0])
        job.cluster_id = cluster_id
        print cluster_id
        job.status = self.get_status(shell, job)
        print job.status
        return job
        

