fab_splunk_deploy
=================

Structure:
-----------------
* fabfile.py: root fab file, it's necesary for fab to run without specifiying a fabfile.
* hosts.yml: yaml file to hold the hosts related values.
* lib:
* * common.py: 
* * host.py: host related funcitons, e.g. host_parser
* * splunk.py: general splunk functinos
* * cluster.py: cluster specfific functions

fab_splunk_deploy