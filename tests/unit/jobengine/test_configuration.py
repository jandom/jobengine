from collections.abc import KeysView

from jobengine import configuration


def struct_to_dict(obj) -> dict:
    if isinstance(obj, configuration.Struct):
        return {key: struct_to_dict(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [struct_to_dict(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(struct_to_dict(item) for item in obj)
    else:
        return obj


def test_create_configuration():
    config = configuration.create_configuration()
    keys = struct_to_dict(config).keys()
    assert keys == KeysView(
        ["engine_file", "private_key_file", "lockers", "rsync", "ssh", "dsa_key"]
    )
