from os import system, path
from time import ctime
from fabric.api import local, run, cd, roles, parallel

# import host arguements
from host import *


@parallel
@roles(run_roles)
def splunk_cmd(exec_cmd=None):
    host_args = host_args_parser(env.host_string)
    exec_cmd = path.join('splunk', 'bin', 'splunk') + ' ' + exec_cmd
    if 'start' or 'stop' or 'restart' or 'status' in exec_cmd:
        exec_cmd += ' --accept-license --no-prompt --answer-yes > /dev/null'
    else:
        exec_cmd += ' -auth admin:changeme'
    cmd(exec_cmd, host_args['deploy_dir'])


@parallel
@roles(run_roles)
def deploy_splunk():
    host_args = host_args_parser(env.host_string)

    # play safe: stop/backup old splunk if it exists.
    #splunk_cmd('stop')
    # if platform = windows, disable boot-start
    # 
    #cmd('rm -rf splunk_bk; mv splunk splunk_bk', host_args['deploy_dir'])

    # deploy pkg
    #put(host_args['pkg'], host_args['deploy_dir'])
    pkg = path.basename(host_args['pkg'])
    print pkg
    if pkg.endswith('.tgz'):
        install_cmd = 'tar -xf %s' %(pkg)
    elif pkg.endswith('.zip'):
        install_cmd = 'unzip -q %s' %(pkg)
    elif pkg.endswith('.Z'):
        install_cmd = 'tar -zxf %s' %(pkg)
    elif pkg.endswith('.msi'):
        install_cmd = 'msiexec /i %s AGREETOLICENSE=Yes /quiet' \
                      %(host_args['pkg'])
    else:
        print "[%s] Unable to handle this pkg %s" %(pkg)
        raise Exception("Unable to handle this pkg, not supported.")
    print install_cmd
    #cmd(install_cmd, host_args['deploy_dir'])


# Dont set roles here, let the execute funciton to handle which role to run.
def setup():
    '''
    setup all machines in run_roles, 
    use execute to run the setup for certain role.
    '''
    for role in run_roles:
        setup_function = 'setup_'+role
        if env.verbose:
            print "[%s] Setting up %s" %(ctime(), role)
        execute(setup_function) # execute will apply its role!


@parallel
@roles(run_roles)
def setup_dist_searchhead():
    pass


@parallel
@roles(run_roles)
def setup_indexer():
    pass


@parallel
@roles(run_roles)
def setup_uforwarder():
    pass


@parallel
@roles(run_roles)
def setup_hwforwarder():
    pass


