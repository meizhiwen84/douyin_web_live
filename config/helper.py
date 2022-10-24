import os
import sys
from pathlib import Path
from ruamel import yaml

def config():
    # settings_file = str(Path(__file__).parent.absolute()) + '/settings.yml'
    settings_file = os.path.join(os.path.dirname(os.path.abspath(os.path.relpath(sys.argv[0]))), "config", "settings.yml")

    with open(settings_file, 'r') as f:
        return yaml.load(f, Loader=yaml.UnsafeLoader)

