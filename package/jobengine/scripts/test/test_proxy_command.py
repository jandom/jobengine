import paramiko

dsa_key = paramiko.DSSKey.from_private_key_file("/home/jandom/.ssh/id_dsa")

conf = paramiko.SSHConfig()
conf.parse(open('/home/jandom/.ssh/config'))
host = conf.lookup('biowulf')
print host

proxy = paramiko.ProxyCommand(host['proxycommand'])

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host["hostname"], username=host["user"], pkey=dsa_key, sock=proxy)


# /usr/local/pbs/bin/qstat
# /usr/local/pbs/bin/qsub  
command = "cd /data/domanskij/.lockers/1c3c2d58-c74c-45e6-bb2e-4e15a708f820; pwd -P; /usr/local/pbs/bin/qsub -h"
(stdin, stdout, stderr) = client.exec_command(command)
print(stdin, stdout, stderr)

print stdout.readlines()
print stderr.readlines()
client.close()
