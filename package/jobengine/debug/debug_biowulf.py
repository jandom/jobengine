

import paramiko


dsa_key = paramiko.DSSKey.from_private_key_file('/home/jandom/.ssh/id_dsa')

conf = paramiko.SSHConfig()
conf.parse(open('/home/jandom/.ssh/config'))
host = conf.lookup('biowulf')
print host['proxycommand']
proxy = paramiko.ProxyCommand(host['proxycommand'])

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("helix.nih.gov", username="domanskij", pkey=dsa_key, sock=proxy)


stdin, stdout, stderr = client.exec_command('ls ~')

print stdout.readlines()

print("client closing")
client.close()
print("client closed")