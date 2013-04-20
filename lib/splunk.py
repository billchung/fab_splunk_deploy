from os import system, path
from time import ctime
from fabric.api import local, run, cd, roles, parallel

# import host arguements
from host import *

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
    host_args = host_parser(env.host_string)
    exec_cmd = path.join('splunk', 'bin', 'splunk') + ' ' + exec_cmd
    if 'start' or 'stop' or 'restart' or 'status' in exec_cmd:
        exec_cmd += ' --accept-license --no-prompt --answer-yes >/dev/null'
    else:
        exec_cmd += ' -auth admin:changeme'
    cmd(exec_cmd, host_args['deploy_dir'])


@parallel
@roles(run_roles)
def deploy_splunk():
    host_args = host_parser(env.host_string)

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
        print "[%s] Unable to handle this pkg %s" %(host_args['pkg'])
        raise Exception("Unable to handle this pkg, not supported.")

    exec_cmd = extract_prefix + path.basename(host_args['pkg'])
    print exec_cmd
    cmd(exec_cmd, host_args['deploy_dir'])

print "imported splunk"