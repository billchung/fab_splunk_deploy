from os import path
from time import ctime
from fabric.api import local, run, cd, roles, parallel, execute

# import host arguements
from host import *


@parallel
@roles(run_roles)
def splunk_cmd(exec_cmd=None):
    '''
    Execute a splunk command at deploy_dir.
    @param: exec_cmd
    '''
    host_args = host_args_parser(env.host_string)
    exec_cmd = path.join('bin', 'splunk')+' '+exec_cmd
    if any(x in exec_cmd for x in ['start', 'restart']):
        exec_cmd += ' --accept-license --no-prompt --answer-yes | grep -v ing'
    else:
        exec_cmd += " -auth {auth}".format(**host_args)
    cmd(exec_cmd, host_args['splunk_dir'])


@parallel
@roles(run_roles)
def splunk_rest(endpoint, args=None):
    '''
    Execute a rest call to remote form localhost.
    @param: endpoint, args
    '''
    host_args = host_args_parser(env.host_string)
    curl_cmd = "curl -k -u {auth} " \
               "https://{hostname}:{splunkd_port}/".format(**host_args) + \
               str(endpoint)
    if args:
        curl_cmd += ' ' + args
    local(curl_cmd)


@parallel
@roles(run_roles)
def deploy_splunk():
    '''
    Deploy splunk pkg, set ports, and start splunk.
    @param: 
    @host_args: is_backup, is_upgrade, is_send_pkg, pkg, deploy_dir, platform, 
    '''
    host_args = host_args_parser(env.host_string)
    splunk_cmd('stop') # play safe: stop existing splunk instance.

    if host_args['is_backup']:
        bk_cmd = "if [[ -d splunk_5 ]]; then " \
                 "  splunk_5/bin/splunk stop > /dev/null; " \
                 "  rm -rf splunk_5; fi; " \
                 "for i in `seq 1 4 | tac`; do " \
                 "  if [[ -d splunk_$i ]]; then " \
                 "    splunk_$i/bin/splunk stop > /dev/null; " \
                 "    mv splunk_$i splunk_$((i+1)); fi; " \
                 "done; cp -r splunk splunk_1" 
        # bk_cmd = "mv splunk splunk_1"
        cmd(bk_cmd, host_args['deploy_dir'])

    if not host_args['is_upgrade']:
        if host_args['platform'].lower() == "windows":
             splunk_cmd("disable boot-start")
        rm_cmd = "rm -rf splunk"
        cmd(rm_cmd, host_args['deploy_dir'])

    if host_args['is_send_pkg']:
        put(host_args['pkg'], host_args['deploy_dir'])

    pkg = path.basename(host_args['pkg'])
    if pkg.endswith('.tgz'):
        install_cmd = 'tar -xf %s' %(pkg)
    elif pkg.endswith('.zip'):
        install_cmd = 'unzip -q %s; cmd /C "icacls splunk /T /C /grant Administrators:f" | grep files' %(pkg)
    elif pkg.endswith('.Z'):
        install_cmd = 'tar -zxf %s' %(pkg)
    elif pkg.endswith('.msi'):
        install_cmd = 'msiexec /i %s AGREETOLICENSE=Yes /quiet' %(pkg)
    else:
        print "[%s] Unable to handle this pkg %s" %(pkg)
        raise Exception("Unable to handle pkg %s, not supported." %(pkg))
    cmd(install_cmd, host_args['deploy_dir'])

    if not host_args['is_upgrade']:
        set_port = "printf '\n[settings]\n" \
                           "mgmtHostPort = 127.0.0.1:{splunkd_port}\n" \
                           "httpport = {splunkweb_port}\n' >> " \
                   "{splunk_dir}/etc/system/local/web.conf".format(**host_args)
        cmd(set_port)
        remote_login = "printf '\n[general]\nallowRemoteLogin=always\n' >> " \
                       "{splunk_dir}/etc/system/local/server.conf".format(**host_args)
        cmd(remote_login)

    splunk_cmd('start')


@parallel
@roles(run_roles)
def put_splunk_file(local, remote):
    '''
    Put file (dir) into remote splunk instance (under $deploy_dir/splunk)
    @params: local path, remote path
    @host_args:
    '''
    host_args = host_args_parser(env.host_string)
    remote_path = path.join(host_args['deploy_dir'], 'splunk', remote)
    put_file(local_path, remote_path)


@parallel
@roles(run_roles)
def get_splunk_file(remote, local):
    '''
    Get file (dir) from remote splunk instance (under $deploy_dir/splunk).
    The file name will append the hostname to its end, to aviod conflicts. 
    @params: remote path, local path
    @host_args:
    '''
    host_args = host_args_parser(env.host_string)
    remote_path = path.join(host_args['deploy_dir'], 'splunk', remote)
    get_file(remote_path, local)


# Dont set roles here, let the execute funciton to handle which role to run.
def setup():
    '''
    Setup all nodes.
    Use execute to run the setup for certain role.
    @param:
    @host_args:
    '''
    for role in run_roles:
        print "[%s] Setting up %s" %(ctime(), role)
        setup_function = 'setup_'+role
        execute(setup_function) # execute will apply its role!

