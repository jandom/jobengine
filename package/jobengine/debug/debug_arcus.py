
from jobengine import clusters
from paramiko import SSHClient
from scp import SCPClient, SCPException

#cluster, shell = clusters.Clusters().get_cluster("arcus-gpu")
cluster = clusters.Clusters().clusters["arcus-gpu"]()
print cluster

if False:
    
    ssh = SSHClient()
    ssh.load_system_host_keys()
    print cluster.hostname
    ssh.connect(cluster.hostname, username=cluster.username)    

if True:
    shell = cluster.connect()

scp = SCPClient(shell.get_transport())
scp.put("dummy", "/tmp", recursive=True)