
import sys
import yaml
from fabric.api import env 

default_roles = ['cluster_master', 'cluster_slave'] # all supported roles
default_deploy_dir = '/home/eserv/'
default_platform = 'Linux' # Linux, Solaris, or Windows
default_port = '8089'
default_web_port = '8000'
default_pkg = 'splunk-5.0.2-155424-SunOS-x86_64.tar.Z'
default_replication_factor = 1
default_search_factor = 1
default_replication_port = 8889
host_arguements = ['host', 'platform', 'deploy_dir', 'port', 'web_port', 'pkg']


'''
deploy_dir, port, web_port, pkg are optional, 
they'll overwirte the default values if exist (in any node)
if the parameters are defined as a list, it'll be used correspondingly.
host needs to be a list.
'''
nodes = {
    'cluster_master': {
        'host':'root@qasus-CentOS-3',
        'platform':'',
        'deploy_dir':'/home/cchung',
    },

    'cluster_searchhead': {
        'host':['eserv@sfeserv43', 'eserv@sfeserv45'],
        'platform':'Windows',
        'deploy_dir':['/home/eserv/cchung', '/home/eserv/cchung'],
        'pkg':'splunk-4.3.6-155455-x64-release.zip'
    },

    'cluster_slave': {
        'host':['root@qasus-CentOS-2', 'Administrator@10.160.44.57', 'Administrator@10.160.44.63'],
        'platform':['Linux', 'windows', 'windows'],
        'deploy_dir':['/home/cchung', '/home/cchung', '/home/cchung'],
        'pkg':['splunk-5.0.2-155424-Linux-x86_64.tgz', 'splunk-5.0.3-157096-x64-release.zip', 'splunk-5.0.3-157096-x64-release.zip']
    }
}


# Arguements
#  1. UF: fwd-server ['host:port', 'host:port' ]
#  2. HWF: fwd-server, listen [ 'tcp:9997', 'udp:9998', 'splunk_tcp:9999']
#  3. IDX: listen [ 'tcp:9997', 'udp:9998', 'splunk_tcp:9999']
#  4. SH: sch-server ['host:port', 'host:port:user:pass']
#  5. cluster_master:
#  6. cluster_searchhead:
#  7. cluster_slave
 

# prase environments 
env.warn_only = True
for node in nodes.keys():
    if type(nodes[node]['host']) == list:
        env.roledefs.update({node:nodes[node]['host']})
    else:
        env.roledefs.update({node:[nodes[node]['host']]})
if "-R" in sys.argv:
    run_roles = sys.argv[sys.argv.index("-R")+1]
else:
    run_roles = default_roles

def host_parser(host):
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

print "imported host"

