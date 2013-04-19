
from os import system, path
from time import ctime
import sys
import yaml
from fabric.contrib.console import confirm
from fabric.api import local, run, cd, env, roles, execute, parallel
from fabric.operations import put

default_roles = ['cluster_master', 'cluster_slave']
default_deploy_dir = '/home/eserv/'
default_platform = 'Linux' # Linux, Solaris, or Windows
default_port = '8089'
default_web_port = '8000'
default_pkg = 'splunk-5.0.2-155424-SunOS-x86_64.tar.Z'
default_replication_factor = 1
default_search_factor = 1
default_replication_port = 8889
host_arguements = ['host', 'platform', 'deploy_dir', 'port', 'web_port', 'pkg']




try:
    from cluster import *
except ImportError, ex:
    print ex






