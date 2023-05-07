from typing import Union

from jobengine.clusters.concrete_clusters import (
    archer,
    arcus,
    arcusb,
    biowulf,
    biowulf2,
    localhost,
)
from jobengine.configuration import Configuration, create_configuration

ConcreteClusters = Union[
    biowulf.Biowulf,
    biowulf2.Biowulf2,
    arcusb.ArcusB,
    arcus.Arcus,
    archer.Archer,
    localhost.Localhost,
]


class ClusterRegistry:
    _cache: dict[str, ConcreteClusters]
    clusters: dict[str, type[ConcreteClusters]]
    configuration: Configuration

    def __init__(
        self,
        *,
        clusters: dict[str, type[ConcreteClusters]],
        configuration: Configuration,
    ):
        self._cache = {}
        self.clusters = clusters
        self.configuration = configuration

    def get_cluster(self, cluster_name: str, /) -> ConcreteClusters:
        cluster_name = cluster_name.lower()

        # check if we have the cluster at all
        assert cluster_name in self.clusters

        # check if we have the cluster in the cache already
        if cluster_name in self._cache:
            return self._cache[cluster_name]

        # create the clusters and populate the cache
        Cluster = self.clusters[cluster_name]
        self._cache[cluster_name] = Cluster()
        return self._cache[cluster_name]


def create_production_cluster_types() -> dict[str, type[ConcreteClusters]]:
    return {
        "biowulf": biowulf.Biowulf,
        "biowulf2": biowulf2.Biowulf2,
        "arcus-b": arcusb.ArcusB,
        "arcus": arcus.Arcus,
        "archer": archer.Archer,
    }


def create_test_cluster_types() -> dict[str, type[ConcreteClusters]]:
    return {
        "localhost": localhost.Localhost,
    }


cluster_registry = ClusterRegistry(
    configuration=create_configuration(),
    clusters=create_production_cluster_types(),
)
