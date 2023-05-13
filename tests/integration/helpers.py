import jobengine.clusters.cluster_registry as cluster_registry
from jobengine import configuration


def create_cluster_registry() -> cluster_registry.ClusterRegistry:
    cluster_types = cluster_registry.create_test_cluster_types()
    registry = cluster_registry.ClusterRegistry(
        clusters=cluster_types,
        configuration=configuration.create_configuration(),
    )
    return registry
