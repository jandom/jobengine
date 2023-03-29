from collections.abc import KeysView
from unittest.mock import patch

import paramiko

from jobengine.clusters.abstract_clusters import base_cluster


# FIXME this is an integration test, ie it really reads from disk
def test_get_host_from_ssh_config():
    ssh_config = base_cluster.get_host_from_ssh_config(hostname="foobar")
    assert ssh_config.keys() == KeysView({"hostname"})


# FIXME this is an integration test, ie it really reads from disk
def test_load_private_key():
    pkey = base_cluster.load_private_key()
    assert isinstance(pkey, (paramiko.DSSKey, paramiko.RSAKey))


@patch("paramiko.SSHClient")
@patch(
    "jobengine.clusters.abstract_clusters.base_cluster.load_private_key",
    return_value="fake-private-key",
)
@patch(
    "jobengine.clusters.abstract_clusters.base_cluster.get_host_from_ssh_config",
    return_value={"hostname": "fake-hostname", "user": "fake-user"},
)
def test_get_paramiko_ssh_client(
    mock_get_host_from_ssh_config, mock_load_private_key, mock_ssh_client
):
    base_cluster.generate_paramiko_ssh_client(hostname="fake-cluster")
    assert mock_get_host_from_ssh_config.call_count == 1
    assert mock_load_private_key.call_count == 1
    assert mock_ssh_client.return_value.connect.call_count == 1


def test_generate_rsync_command():
    cmd = base_cluster.generate_rsync_command(proxy="jump-host-hostname", verbose=True)
    assert (
        cmd
        == "/usr/bin/rsync --compress -e ssh -q jump-host-hostname ssh -v --progress -a"
    )
