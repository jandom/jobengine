import os
import pathlib
from dataclasses import dataclass
from typing import Optional

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from jobengine.model.job import Job


@dataclass
class Configuration:
    engine_file: str
    lockers_directory: str
    rsync_flags: str


def _make_configuration(
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
    config = _make_configuration(path=path)
    _initialize_database(config=config)
    return config


def _initialize_database(config: Configuration):
    if not pathlib.Path(config.engine_file).exists():
        engine = sqlalchemy.create_engine(config.engine_file)
        Job.metadata.create_all(engine)


def create_session():
    config = create_configuration()
    engine = sqlalchemy.create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    return Session()
