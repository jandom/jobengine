import logging
import os
import subprocess
from typing import Optional, Union

import paramiko

from jobengine import configuration, job
from jobengine.status import Status


def get_host_from_ssh_config(*, hostname: str) -> paramiko.SSHConfigDict:
    # load and parse SSH config file
    ssh_config_file = "{}/.ssh/config".format(os.environ["HOME"])
    ssh_config = paramiko.SSHConfig()
    with open(ssh_config_file) as f:
        ssh_config.parse(f)
    host = ssh_config.lookup(hostname=hostname)
    return host


def load_private_key() -> Union[None, paramiko.DSSKey, paramiko.RSAKey]:
    # load private DSA/RSA key
    dsa_private_key_file = os.path.join(os.environ["HOME"], ".ssh", "id_dsa")
    rsa_private_key_file = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")
    dsa_key, rsa_key = None, None
    if os.path.exists(dsa_private_key_file):
        dsa_key = paramiko.DSSKey.from_private_key_file(dsa_private_key_file)
    if os.path.exists(rsa_private_key_file):
        rsa_key = paramiko.RSAKey.from_private_key_file(rsa_private_key_file)
    if not (rsa_key or dsa_key):
        raise RuntimeError(
            "Neither DSA nor RSA key found in {} {}".format(
                dsa_private_key_file, rsa_private_key_file
            )
        )
    pkey = dsa_key or rsa_key
    return pkey


def generate_paramiko_ssh_client(*, hostname: str) -> paramiko.SSHClient:
    host = get_host_from_ssh_config(hostname=hostname)
    pkey = load_private_key()

    # create client
    client = paramiko.SSHClient()
    client.load_system_host_keys()

    proxy = (
        paramiko.ProxyCommand(host["proxycommand"])
        if host and "proxycommand" in host
        else None
    )

    client.connect(
        hostname=host["hostname"] if "hostname" in host else hostname,
        username=host["user"] if "user" in host else None,
        pkey=pkey,
        sock=proxy,  # type: ignore
        timeout=1000,
    )
    return client


def generate_rsync_command(*, proxy: Optional[str], verbose: bool = True) -> str:
    verbose_flags = "-v --progress" if verbose else "-v"
    proxy = "ssh -q {proxy} ssh".format(proxy=proxy) if proxy else "ssh -q"
    config = configuration.create_configuration()
    cmd = "/usr/bin/rsync --compress -e {proxy} {verbose_flags} {flags}".format(
        proxy=proxy,
        verbose_flags=verbose_flags,
        flags=config.rsync_flags,
    )
    return cmd


class BaseCluster:
    name: str
    hostname: str
    username: str
    proxy: Optional[str] = None
    shell: Optional[paramiko.SSHClient] = None
    path: str
    configuration: configuration.Configuration

    def __repr__(self):
        return "<Cluster '%s' %s@%s:%s>" % (
            self.name,
            self.username,
            self.hostname,
            self.proxy,
        )

    def get_status(self, job: job.Job, /) -> Status:
        raise NotImplementedError

    def cancel(self, job: job.Job, /) -> None:
        raise NotImplementedError

    def launch(
        self, shell: paramiko.SSHClient, job: job.Job, /, **kwargs
    ) -> tuple[list[str], list[str]]:
        raise NotImplementedError

    def submit(self, job: job.Job, /, **kwargs) -> None:
        raise NotImplementedError

    def run_shell_command(self, cmd: str, /) -> tuple[list[str], list[str]]:
        shell = self.get_shell()
        (_, stdout, stderr) = shell.exec_command(cmd)
        return (stdout.readlines(), stderr.readlines())

    def delete(self, job: job.Job, /) -> None:
        cmd = "mv ~/.lockers/{} ~/.trash".format(job.uuid)
        logging.info(cmd)
        stdout, stderr = self.run_shell_command(cmd)
        logging.debug((stdout, stderr))

    def pull(self, job: job.Job, /, *, verbose=False) -> bytes:
        cmd = "{rsync} {hostname}:{remote_path}/.lockers/{uuid}/* {local_path}/.lockers/{uuid}/ ".format(
            rsync=generate_rsync_command(proxy=self.proxy, verbose=verbose),
            hostname=self.hostname,
            local_path=job.local_workdir,
            remote_path=job.remote_workdir,
            uuid=job.uuid,
        )
        cmd += " --include='*.xtc' --include='*.trr' --include='*.gro' --include='*.mdp' --include='*.sh'  --include='*GRID*' --include='*HILLS*' --include='*COLVAR*' --include='*colvar*' --include='*.cpt' --include='*.dat'  --include='*.log' --include='*.ndx' --include='*.edr'  --include='*.qvt' --exclude='*.*' "
        return subprocess.check_output(cmd.split(" "))

    def push(self, job: job.Job, /, *, verbose=False) -> bytes:
        # return subprocess.check_output(["ls", "-la", job.local_workdir + "/.lockers/fake-uuid/"])
        cmd = "{rsync} {local_path}/.lockers/{uuid}/ {hostname}:{remote_path}/.lockers/{uuid}".format(
            rsync=generate_rsync_command(proxy=self.proxy, verbose=verbose),
            uuid=job.uuid,
            hostname=self.hostname,
            local_path=job.local_workdir,
            remote_path=job.remote_workdir,
        )
        return subprocess.check_output(cmd.split(" "))

    def get_shell(self) -> paramiko.SSHClient:
        if self.shell:
            return self.shell
        self.shell = generate_paramiko_ssh_client(hostname=self.hostname.lower())
        return self.shell
