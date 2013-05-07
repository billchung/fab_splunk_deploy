import sys
import yaml
from os import path
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


# Role is specified in sys.argv?
if "-R" in sys.argv:
    run_roles = sys.argv[sys.argv.index("-R")+1]
else:
    run_roles = []
    for node in hosts_arg['nodes']:
        run_roles.append(node['role'])


# hosts_arg
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
            for key in hosts_arg['host_params']:
                if key in node: # if key is defined in role-level
                    if type(node[key]) == list: # for a specific host
                        args.update({key:node[key][pos]})
                    elif type(node[key]) == str or int: # for all hosts of a role
                        args.update({key:node[key]})
                    else: 
                        raise Exception("Argument should be list, str, or int!")
                else: # not defined in role-level, apply default value
                    args.update({key:hosts_arg["default_"+key]})
        else: # host is not in this node/role
            continue # not necessary, just to be clearer.

    if args['pkg'].startswith('splunkforwarder'):
        splunk_dir = path.join(args['deploy_dir'], 'splunkforwarder')
    else:
        splunk_dir = path.join(args['deploy_dir'], 'splunk')

    if "@" in args['host']:
        user, hostname = args['host'].split("@")
    else:
        user, hostname = '', args['host']
    args.update({'splunk_dir':splunk_dir, 'user': user, 'hostname':hostname})

    if env.debug: 
        print "Host args of %s:\n%s" %(host, args)
    return args


def _path_join(platform, *args):
    if platform.lower() == "windows":
        print "\\\\".join(args)
    else:
        print "/".join(args)


@parallel
@roles(run_roles)
def cmd(exec_cmd=None, directory=''):
    '''
    Issue a command to remote shell.
    @param: cmd, issue directory.
    '''
    if directory: # play safe: create dir if it doesnt exist.
        cmd('mkdir -p %s' %(directory))
    with cd(directory):
        if env.verbose:
            print ' - [%s] In [%s:%s] exec_cmd [%s]' %(
                   ctime(), env.host_string, directory, exec_cmd)
        run(exec_cmd)


@parallel
@roles(run_roles)
def put_file(local, remote):
    '''
    Put file or dir to remote host.
    @param: local path, remote path
    '''
    if env.verbose:
        print ' - [%s] Put [%s] to [%s:%s]' %(
                   ctime(), local, env.host_string, remote)
    put(local, remote)


@parallel
@roles(run_roles)
def get_file(remote, local):
    '''
    Get file or dir to remote host.
    The file name will append the hostname to its end, to aviod conflicts. 
    @param: remote path, local path

    '''
    local_path = path.join(local, path.basename(remote)+'_'+env.host_string)
    if env.verbose:
        print ' - [%s] Get [%s] from [%s:%s]' %(
                   ctime(), local_path, env.host_string, remote)
    get(remote, local_path)



