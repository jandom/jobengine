from enum import Enum


class Status(str, Enum):
    Running = "R"
    Cancelled = "C"
    Stopped = "S"
    Queued = "Q"
    Pending = "PD"
    Unknown = "U"
