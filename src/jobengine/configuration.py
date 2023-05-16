import os
import pathlib
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import create_engine

from jobengine.model.job import Job


@dataclass
class Configuration:
    engine_file: str
    lockers_directory: str
    rsync_flags: str


def make_configuration(
    path: Optional[pathlib.Path] = None, rsync_flags: str = "-a --compress"
) -> Configuration:
    if not path:
        path = pathlib.Path(os.path.expanduser("~"))
    lockers_directory = path / ".lockers"
    if not lockers_directory.exists():
        lockers_directory.mkdir()
    engine_file = lockers_directory / "jobengine.sql"
    config = Configuration(
        engine_file=f"sqlite:///{engine_file}",
        lockers_directory=str(lockers_directory),
        rsync_flags=rsync_flags,
    )
    return config


def create_configuration(path: Optional[pathlib.Path] = None) -> Configuration:
    config = make_configuration(path=path)
    initialize_database(config=config)
    return config


def initialize_database(config: Configuration):
    if not pathlib.Path(config.engine_file).exists():
        engine = create_engine(config.engine_file)
        Job.metadata.create_all(engine)
