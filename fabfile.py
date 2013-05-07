from os import path
import yaml
from fabric.api import env
from fabric.state import output

properties_yml = path.join(path.dirname(path.realpath(__file__)), 'properties.yml')
properties = yaml.load(open(properties_yml))

env.debug = properties['debug']
env.verbose = properties['verbose']
env.warn_only = properties['warn_only']

# Modify fab output level
for key in output.keys():
    output[key] = properties[key]

try:
    from lib.cluster import *
    from lib.splunk import *
except ImportError, ex:
    print ex


