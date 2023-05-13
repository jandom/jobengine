import os
import pathlib
from dataclasses import dataclass


@dataclass
class Configuration:
    engine_file: str
    lockers_directory: str
    rsync_flags: str


def create_configuration() -> Configuration:
    lockers_directory = pathlib.Path(os.path.expanduser("~")) / ".lockers"
    if not lockers_directory.exists():
        lockers_directory.mkdir()
    engine_file = f"sqlite:///{lockers_directory}/jobengine.sql"
    config = Configuration(
        engine_file=engine_file,
        lockers_directory=str(lockers_directory),
        rsync_flags="-a",  # --compress",
    )
    return config
