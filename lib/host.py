import sys
import yaml
from os import system, path
from time import ctime
from fabric.api import local, run, put, get, cd, env, roles, parallel


# prase environments 
fab_home_path = path.join(path.dirname(path.realpath(__file__)), '..')
hosts_yml = path.join(fab_home_path, 'hosts.yml')
hosts_arg = yaml.load(open(hosts_yml))

for node in hosts_arg['nodes']:
    if type(node['host']) == list:
        env.roledefs.update({node['role']:node['host']})
    elif type(node['host']) == str:
        env.roledefs.update({node['role']:[node['host']]})
    else:
        raise Exception("Host arg needs to be list or str! error @host: %s" 
                        %arg['host'])
if "-R" in sys.argv:
    run_roles = sys.argv[sys.argv.index("-R")+1]
else:
    run_roles = hosts_arg['run_roles']

# host_arg
# {'default_roles': ['cluster_master', 'cluster_slave'], 
#  'default_with_data': False, 
#  'default_pkg': 'splunk-5.0.2-155424-SunOS-x86_64.tar.Z', 
#  ...
#  'nodes': [
#     {'deploy_dir': '/export/home/eserv/cchung', 'platform': 'Linux', 'host': 'root@qasus-CentOS-5', 'splunkweb_port': '8000', 'role': 'cluster_master', 'pkg': 'splunk-5.0.2-155424-SunOS-x86_64.tar.Z', 'splunkd_port': '8089'}, 
#     {'deploy_dir': ['/home/eserv/', '/home/cchung'], 'platform': '', 'host': ['eserv@sfeserv44', 'eserv@sfeserv45'], 'splunkweb_port': '8000', 'role': 'cluster_searchhead', 'pkg': None, 'splunkd_port': '8089'}, 
#     {'deploy_dir': ['/home/cchung', '/home/cchung', '/home/cchung'], 'platform': ['Linux', 'windows', 'windows'], 'host': ['root@qasus-CentOS-4', 'Administrator@10.160.44.57', 'Administrator@10.160.44.63'], 'role': 'cluster_slave', 'pkg': ['splunk-5.0.2-155424-Linux-x86_64.tgz', 'splunk-5.0.3-157096-x64-release.zip', 'splunk-5.0.3-157096-x64-release.zip']}
#  ], 
# }
# Parse:
# {'deploy_dir': '/home/cchung', 'platform': 'windows', 'host': 'Administrator@10.160.44.57', 'splunkweb_port': '8000', 'pkg': 'splunk-5.0.3-157096-x64-release.zip', 'splunkd_port': '8089'}

def host_args_parser(host):
    '''
    Parse the host arguements as dict.
    Host argeuments will overwrite the defaults, 
    it'll find the corresponding positions if it was defined as a list.
    '''
    args = {}

    # find the position(index) and values for a host.
    for node in hosts_arg['nodes']:
        if host in node['host']: # found what role this host belongs to
            pos = node['host'].index(host) # find its position
            for key in hosts_arg['host_arguments']:
                if key in node: # if key is defined in role-level
                    if type(node[key]) == list: # for a specific host
                        args.update({key:node[key][pos]})
                    elif type(node[key]) == str: # for all hosts of a role
                        args.update({key:node[key]})
                    else: 
                        raise Exception("Argument needs to be list or str!")
                else: # not defined in role-level, apply default value
                    args.update({key:hosts_arg["default_"+key]})
        else: # host is not in this node/role
            continue # not necessary, just to be clear.
    if env.verbose: 
        print "Host args of %s:\n%s" %(host, args)
    return args


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
        if env.verbose:
            print ' - [%s] In [%s] exec_cmd [%s]' %(ctime(), directory, exec_cmd)
        run(exec_cmd)



@parallel
@roles(run_roles)
def put_file(local, remote):
    put(local, remote)


@parallel
@roles(run_roles)
def get_file(remote, local):
    local_path = path.join(local, path.basename(remote)+'_'+env.host_string)
    get(remote, local_path)


@parallel
@roles(run_roles)
def put_splunk_file(local, remote):
    host_args = host_args_parser(env.host_string)
    remote_path = path.join(host_args['deploy_dir'], remote)
    put(local_path, remote_path)

@parallel
@roles(run_roles)
def get_splunk_file(remote, local):
    host_args = host_args_parser(env.host_string)
    remote_path = path.join(host_args['deploy_dir'], remote)
    local_path = path.join(local, path.basename(remote)+'_'+env.host_string)
    get(remote_path, local_path)
