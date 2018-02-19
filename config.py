import os
import yaml

path = __file__
if path.endswith('.pyc') and os.path.exists(path[:-1]):
    path = path[:-1]

path = os.path.realpath(path)

with open(os.path.join(os.path.dirname(path), 'config.yaml')) as fs:
    config = yaml.load(fs)
