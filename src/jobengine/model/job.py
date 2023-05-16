from typing import Optional

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from jobengine.status import Status


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    uuid: Mapped[str] = mapped_column(String)
    workdir: Mapped[str] = mapped_column(String)
    local_workdir: Mapped[str] = mapped_column(String)
    remote_workdir: Mapped[str] = mapped_column(String)
    cluster_name: Mapped[str] = mapped_column(String)
    cluster_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    nodes: Mapped[int] = mapped_column(Integer)
    partition: Mapped[Optional[str]] = mapped_column(String)
    current_chemtime: Mapped[float] = mapped_column(Float)
    target_chemtime: Mapped[float] = mapped_column(Float)

    def __init__(
        self,
        *,
        name: str,
        uuid: str,
        workdir: str,
        local_workdir: str,
        remote_workdir: str,
        cluster_name: str,
        cluster_id: int,
        status: Status = Status.Unknown,
        nodes: int = 1,
        partition: str = "",
        current_chemtime: float = 0.0,
        target_chemtime: float = 0.01,  # make this tiny, but non-zero, to prevent a non-started job from being considered finished
    ):
        self.name = name
        self.uuid = uuid
        self.workdir = workdir
        self.local_workdir = local_workdir
        self.remote_workdir = remote_workdir
        self.cluster_name = cluster_name
        self.cluster_id = cluster_id
        self.status = status
        self.nodes = nodes
        self.partition = partition
        self.current_chemtime = current_chemtime
        self.target_chemtime = target_chemtime

    def __repr__(self):
        return (
            "<Job '%s Cluster: %s'>\n\tId: %d Cluster Id: %d Status: %s UUID: %s\n\tWorkdir: %s\n\tRemote workdir: %s"
            % (
                self.name,
                self.cluster_name,
                self.id if self.id else 0,
                self.cluster_id if self.cluster_id else 0,
                self.status,
                self.uuid,
                self.workdir,
                self.remote_workdir,
            )
        )
