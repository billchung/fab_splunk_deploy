from os import system, path
import sys
from fabric.contrib.console import confirm
from fabric.api import local, run, cd, env, roles, execute, parallel
from fabric.operations import put
# import host arguements
from host import *
from splunk import *


@roles('cluster_master')
def setup_cluster_master():
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    conf_string = "\n[clustering]\nmode = master\n"
    conf_string +="replication_factor = {0}\nsearch_factor = {1}\n".format(
                   default_replication_factor, default_search_factor)
    conf_file = path.join('splunk', 'etc', 'system', 'local', 'server.conf')
    exec_cmd = 'printf "%s" >> %s ' %(conf_string, conf_file)
    cmd(exec_cmd, host_args['deploy_dir'])
    splunk_cmd('start')


@parallel
@roles('cluster_searchhead')
def setup_cluster_searchhead():
    print env
    host_args = host_args_parser(env.host_string)
    print "current node = %s" %host_args['host']
    print "master node = %s" %nodes['cluster_master']['host'][0].split("@")[1]
    #deploy_splunk(host_args)
    #print "[%s] Start setting up sh: %s" %(ctime(), nodes[env.roles[0]])


@parallel
@roles('cluster_slave')
def setup_cluster_slave():
    host_args = host_args_parser(env.host_string)
    master_node = nodes['cluster_master']['host'][0]
    deploy_splunk()
    conf_string = "\n[replication_port://%s]\n" %(default_replication_port)
    conf_string += "\n[clustering]\nmode = slave\n"
    conf_string += "master_uri = https://{0}:{1}".format(
                   'sfeserv43', '8089')
    conf_file = path.join('splunk', 'etc', 'system', 'local', 'server.conf')
    exec_cmd = 'printf "%s" >> %s ' %(conf_string, conf_file)
    cmd(exec_cmd, host_args['deploy_dir'])
    splunk_cmd('start')


