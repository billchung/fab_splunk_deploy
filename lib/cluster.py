
from fabric.contrib.console import confirm
from fabric.api import local, run, cd, env, roles, execute, parallel
from fabric.operations import put
# import host arguements
from host import *
from splunk import *


@parallel
@roles('cluster_master')
def setup_cluster_master():
    '''
    Setup cluster master node.
    '''
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    edit_cmd = "edit cluster-config -mode master " \
               "-replication_factor {replication_factor} " \
               "-search_factor {search_factor} " \
               "-auth {auth}".format(**host_args)
    splunk_cmd(edit_cmd)
    splunk_cmd('restart')


@parallel
@roles('cluster_searchhead')
def setup_cluster_searchhead():
    '''
    Setup cluster searchhead node.
    '''
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    edit_cmd = "edit cluster-config -mode searchhead " \
               "-master_uri https://{master_uri} " \
               "-auth {auth}".format(**host_args)
    splunk_cmd(edit_cmd)
    splunk_cmd('restart')


@parallel
@roles('cluster_slave')
def setup_cluster_slave():
    '''
    Setup cluster slave (peer) node.
    '''
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    edit_cmd = "edit cluster-config -mode slave " \
               "-master_uri https://{master_uri} " \
               "-replication_port {replication_port} " \
               "-auth {auth}".format(**host_args)
    splunk_cmd(edit_cmd)
    splunk_cmd('restart')


