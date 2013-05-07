from os import path
import sys
from fabric.contrib.console import confirm
from fabric.api import local, run, cd, env, roles, execute, parallel
from fabric.operations import put
# import host arguements
from host import *
from splunk import *


@parallel
@roles('searchhead')
def setup_searchhead():
    '''
    Setup searchhead node
    @param: 
    @host_args: search_server
    '''
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    for s_server in host_args['search_server']:
        if len(s_server.split(':')) == 2:
            [s_host, s_port] = s_server.split(':')
            [s_user, s_pass] = host_args['auth'].split(':')
        elif len(s_server.split(':')) == 4:
            [s_host, s_port, s_user, s_pass] = s_server.split(':')
        splunk_cmd('add search-server %s:%s -remoteUsername %s -remotePassword %s'
                   %(s_host, s_port, s_user, s_pass))


@parallel
@roles('indexer')
def setup_indexer():
    '''
    Setup indexer node
    @param: 
    @host_args: listen_type_port, is_with_data, deploy_dir, data_file
    '''
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    for listen in host_args['listen_type_port']:
        [listen_type, listen_port ] = listen.split(':')
        if listen_type == 'splunktcp':
            splunk_cmd('enable listen %s' %(listen_port))
        elif listen_type == 'tcp':
            splunk_cmd('add tcp %s' %(listen_port))
        elif listen_type == 'udp':
            splunk_cmd('add udp %s' %(listen_port))
        else:
            print "[%s] Not supported type %s" %(listne_type)

    if host_args['is_with_data']:
        put(host_args['data_file'], host_args['deploy_dir'])
        remote_data = path.join(host_args['deploy_dir'], 
                                path.basename(host_args['data_file']))
        splunk_cmd('add monitor %s' %remote_data)


@parallel
@roles('forwarder')
def setup_forwarder():
    '''
    Setup fowarder node
    @param:
    @host_args:
    '''
    host_args = host_args_parser(env.host_string)
    deploy_splunk()
    for f_server in host_args['forward_server']:
        splunk_cmd('add forward-server %s' %(f_server))

    if host_args['is_with_data']:
        put(host_args['data_file'], host_args['deploy_dir'])
        remote_data = path.join(host_args['deploy_dir'], 
                                path.basename(host_args['data_file']))
        splunk_cmd('add monitor %s' %remote_data)
