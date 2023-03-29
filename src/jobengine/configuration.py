import os


class Struct:
    """The recursive class for building and representing objects with."""

    def __init__(self, obj):
        for k, v in list(obj.items()):
            if isinstance(v, dict):
                setattr(self, k, Struct(v))
            else:
                setattr(self, k, v)

    def __getitem__(self, val):
        return self.__dict__[val]

    def __repr__(self):
        return "{%s}" % str(
            ", ".join(
                "%s : %s" % (k, repr(v)) for (k, v) in list(self.__dict__.items())
            )
        )


def create_configuration():
    lockers_directory = os.path.join(os.environ["HOME"], ".lockers")
    engine_file = f"sqlite:///{lockers_directory}/jobengine.sql"
    config = {
        "engine_file": engine_file,
        "private_key_file": os.path.join(os.environ["HOME"], ".ssh", "id_dsa"),
        "lockers": lockers_directory,
        "rsync": {
            "flags": "-a",  # --compress",
        },
        "ssh": None,
        "dsa_key": None,
    }
    config = Struct(config)
    return config


config = create_configuration()
