import json
import os


CONFIG_FILE_PATH = os.path.join(os.path.expanduser('~'), '.config', 'gpy', 'config.json')


def import_config(path=CONFIG_FILE_PATH):
    """Import JSON configuration file."""
    with open(path) as fd:
        config = json.load(fd)
    return config
