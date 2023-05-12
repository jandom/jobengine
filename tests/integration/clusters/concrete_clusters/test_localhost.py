import pathlib

from scp import SCPClient

from tests.integration.helpers import create_cluster_registry


def test_run_shell_command():
    cluster_registry = create_cluster_registry()
    cluster = cluster_registry.get_cluster("localhost")
    stdout, _ = cluster.run_shell_command("ls ~")

    assert len(stdout.readlines()) > 0


def test_scp_put():
    cluster_registry = create_cluster_registry()
    cluster = cluster_registry.get_cluster("localhost")
    shell = cluster.get_shell()
    dummy_path = pathlib.Path(__file__).parent.parent.parent / "data" / "dummy"
    scp = SCPClient(shell.get_transport())
    scp.put(dummy_path, "/tmp", recursive=True)
