from typing import Union

from jobengine.clusters.concrete_clusters import (
    archer,
    arcus,
    arcusb,
    biowulf,
    biowulf2,
    localhost,
)

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

    def __init__(self, clusters: dict[str, type[ConcreteClusters]]):
        self._cache = {}
        self.clusters = clusters

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


cluster_registry = ClusterRegistry(
    clusters={
        "biowulf": biowulf.Biowulf,
        "biowulf2": biowulf2.Biowulf2,
        "arcus-b": arcusb.ArcusB,
        "arcus": arcus.Arcus,
        "archer": archer.Archer,
        "localhost": localhost.Localhost,
    },
)