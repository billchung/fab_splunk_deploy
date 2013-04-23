from os import system, path
import sys
from fabric.contrib.console import confirm
from fabric.api import local, run, cd, env, roles, execute, parallel
from fabric.operations import put
# import host arguements
from host import *
from splunk import *

@parallel
@roles('dist_searchhead')
def setup_dist_searchhead():
    pass


@parallel
@roles('dist_searchpeer')
def setup_dist_searchpeer():
    pass
