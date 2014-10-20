#script for cronjob, sync perforce and look for new workarounds.
#For example, add it like:
# m h  dom mon dow   command
#10 17 * * * /usr3/dev/experiments/wa_parser/p4_update_n_parse.sh

export P4HOST=<HOSTNAME>
export P4PORT=<perforce-server:port>
export P4USER=<username>
export P4PASSWD=<YOURPASSWORD>
export P4CLIENT=<p4_workspace_name>
export P4CHARSET=utf8
echo $P4PASSWD| p4 login
p4 sync //$P4CLIENT/path/to_source/...
p4 logout
cd /usr3/dev/experiments/wa_parser
# then run python parse.py...
