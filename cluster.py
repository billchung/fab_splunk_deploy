from os import system, path
from time import ctime
import sys
import yaml
from fabric.contrib.console import confirm
from fabric.api import local, run, cd, env, roles, execute, parallel
from fabric.operations import put

from host import *

def _host_parser(host):
    '''
    Parse the host arguements as dict.
    host argeuments will overwrite the defaults, 
    and it'll find the corresponding positions if it was defined as a list.
    '''
    host_args = {}

    # find what's the role and where the index is.
    for role in nodes:
        if host in nodes[role]['host']:
            index = nodes[role]['host'].index(host)
            host_role = role

    # get the values.
    for key in host_arguements:
        if key in nodes[host_role]: # if the host has the arguement, apply it.
            if type(nodes[host_role][key]) == list: # list of values
                host_args.update({key:nodes[host_role][key][index]})
            elif type(nodes[host_role][key]) == str: # single value
                host_args.update({key:nodes[host_role][key]})
            else: # not able to handle, 
                raise 
        else: # if the host doesnt have the key, apply default value.
            host_args.update({key:eval("default_"+key)})
    return host_args


def _path_join(platform, *args):
    if platform.lower() == "windows" or "win" or "win32" :
        print "\\\\".join(args)
    else:
        print "/".join(args)


@parallel
@roles(run_roles)
def cmd(exec_cmd=None, directory=''):
    if directory: # play safe: create dir if it doesnt exist.
        cmd('mkdir -p %s' %(directory))
    with cd(directory):
        print ' - [%s] In [%s] exec_cmd [%s]' %(ctime(), directory, exec_cmd)
        run(exec_cmd)


@parallel
@roles(run_roles)
def splunk_cmd(exec_cmd=None):
    host_args = _host_parser(env.host_string)
    exec_cmd = path.join('splunk', 'bin', 'splunk') + ' ' + exec_cmd
    if 'start' or 'stop' or 'restart' or 'status' in exec_cmd:
        exec_cmd += ' --accept-license --no-prompt --answer-yes >/dev/null'
    else:
        exec_cmd += ' -auth admin:changeme'
    cmd(exec_cmd, host_args['deploy_dir'])


@parallel
@roles(run_roles)
def deploy_splunk():
    host_args = _host_parser(env.host_string)

    # play safe: stop/backup old splunk if it exists.
    splunk_cmd('stop')
    # if platform = windows, disable boot-start
    # 
    cmd('rm -rf splunk_bk; mv splunk splunk_bk', host_args['deploy_dir'])

    # deploy pkg
    put(host_args['pkg'], host_args['deploy_dir'])
    if host_args['pkg'].endswith('.tgz'):
        extract_prefix = 'tar -xf '
    elif host_args['pkg'].endswith('.zip'):
        extract_prefix = 'unzip -q '
    elif host_args['pkg'].endswith('.Z'):
        extract_prefix = 'tar -zxf '
    # elif .msi, use msiexec to install, 
    # extract_prefix = 'msiexec /i pkg PARAM /quiet'
    else:
        print "[%s] Unable to handle(untar) this pkg %s" %(host_args['pkg'])

    exec_cmd = extract_prefix + path.basename(host_args['pkg'])
    print exec_cmd
    cmd(exec_cmd, host_args['deploy_dir'])


# Dont apply any role here, let the execute funciton to handle roles to run.
def setup():
    '''
    setup all machines in run_roles, 
    use execute to run the setup for certain role.ma
    '''
    for node_type in run_roles:
        setup_function = 'setup_'+node_type
        print "[%s] Setting up %s" %(ctime(), node_type)
        execute(setup_function) # execute will apply its role!


@roles('cluster_master')
def setup_cluster_master():
    host_args = _host_parser(env.host_string)
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
    host_args = _host_parser(env.host_string)
    print "current node = %s" %host_args['host']
    print "master node = %s" %nodes['cluster_master']['host'][0].split("@")[1]
    #deploy_splunk(host_args)
    #print "[%s] Start setting up sh: %s" %(ctime(), nodes[env.roles[0]])


@parallel
@roles('cluster_slave')
def setup_cluster_slave():
    host_args = _host_parser(env.host_string)
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


@parallel
@roles('dist_searchhead')
def setup_dist_searchhead():
    pass


@parallel
@roles('dist_searchpeer')
def setup_dist_searchpeer():
    pass

