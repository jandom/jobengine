import pathlib

from scp import SCPClient

import jobengine.clusters.cluster_registry as cluster_registry


def test_exec_command():
    cluster = cluster_registry.cluster_registry.get_cluster("localhost")
    shell = cluster.get_shell()
    (_, stdout, stderr) = shell.exec_command("ls ~")
    assert len(stdout.readlines()) > 0


def test_scp_put():
    cluster = cluster_registry.cluster_registry.get_cluster("localhost")
    shell = cluster.get_shell()
    dummy_path = pathlib.Path(__file__).parent.parent.parent / "data" / "dummy"
    scp = SCPClient(shell.get_transport())
    scp.put(dummy_path, "/tmp", recursive=True)