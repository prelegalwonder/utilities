#Creates a maintenance period in Zabbix, outputs the ID to a text file, then deletes the maintenance period and file when you run with -r

import sys
import urllib2
import optparse
import json
import time
import os

parser = optparse.OptionParser()
parser.add_option ("-g", "--group", dest="group",
					help="group you'd like to put into or remove from maintenance")
#parser.add_option ("-h", "--host", dest="group",
#					help="Host you'd like to put into or remove from maintenance")					
parser.add_option ("-r", "--remove", action="store_true", dest="remove",
					help="Remove a group from maintenance")
parser.add_option ("-a", "--add", action="store_true", dest="add",
					help="Add a maintenance period for a group")
parser.add_option ("-d", "--duration", dest="duration", type="float", default="10800",
					help="Length of downtime in seconds, default is 10800 or 3 hours.  3600 for 1 hour, 7200 for 2 hours")
parser.add_option ("-s", "--server", dest="server", default="http://cnxmonitor.mgmt.cnxprod.com/zabbix/api_jsonrpc.php",
					help="zabbix server, default is cnxmonitor")
parser.add_option ("-u", "--user", dest="user", default="api_user",
					help="api user, default is api_user")
parser.add_option ("-p", "--password", dest="password", default="Zb><8p1",
					help="password.  Default is zabbix api_user password")
					
(options, args) = parser.parse_args()	

def authenticate(srv, usr, pwd):
	authdata = json.dumps({"jsonrpc":"2.0","method":"user.login","params":{"user":usr,"password":pwd},"id":"1"})
	print "authenticating to " + srv
	req = urllib2.Request(srv, authdata, headers = {'Content-Type': 'application/json'})
	resp = urllib2.urlopen(req)
	output = resp.read()
	
	pairs = output.split(',')[1]
	authkey = pairs.split(':')[1]
	authkey = authkey[1:-1]
	print "You have been authenticated"
	return authkey;

def getgroupid(gid, key, srv):
	print "Getting your group ID from Zabbix"
	getid = json.dumps({"jsonrpc":"2.0","method":"hostgroup.get","params":{"filter":{"name":gid},},"auth":key,"id":"2"})
	gidreq = urllib2.Request(srv, getid, headers = {'Content-Type': 'application/json'})
	gidpost = urllib2.urlopen(gidreq)
	gidout = gidpost.read()
	gidpairs = gidout.split(',')[1]
	gid = gidpairs.split(':')[2]
	gid = gid[1:-3]
	print "Success, your group id is " + gid
	return gid;
	
def create(gid, dur, key, srv, client):
	print "Creating a maintenance period now for " + client
	now = time.time() - 60
	nowint=int(float(now))
	nowstr=str(float(now))
	createmaint = json.dumps({"jsonrpc":"2.0","method":"maintenance.create","params":[{"groupids":[gid],"name":"maintenance for " + client + " " + nowstr,"maintenance_type":"0","description":"maintenance for " + client + " for " + " " + nowstr, "active_since":nowint,"active_till":nowint + dur + 100,"timeperiods":[{"timeperiod_type":"0","start_date":nowint,"period":dur}],}],"id":"3","auth":key})
	maintreq = urllib2.Request(srv, createmaint, headers = {'Content-Type': 'application/json'})
	maintpost = urllib2.urlopen(maintreq)
	maintout = maintpost.read()
	maintpairs = maintout.split(',')[1]
	maintid = maintpairs.split(':')[2]
	maintid = maintid[2:-3]
	mtid = open ('mtid.txt', 'w')
	mtid.write(maintid)
	mtid.close()
	print "Successfully created a maintenance period with an id of " + maintid
	return maintid
	
def remove(key, maintid, srv):
	print "removing your maintenance period"
	remmaint = json.dumps({"jsonrpc":"2.0","method":"maintenance.delete","params":[maintid],"auth":key,"id":"4"})
	remmaintreq = urllib2.Request(srv, remmaint, headers = {'Content-Type': 'application/json'})
	remmaintpost = urllib2.urlopen(remmaintreq)
	remmaintout = remmaintpost.read()
	print "Maintenace removal - Zabbix response was " + remmaintout
	mtid = open ('mtid.txt', 'r')
	mid = mtid.read()
	mtid.close()
	if '"maintenanceids":["' + mid in remmaintout:
		print "Maintenance removed succesfully"	
	else:
		print "ERROR! Maintenance not removed, please remove manually."
		sys.exit(1)
	
	
	
key = authenticate(options.server, options.user, options.password);
gid = getgroupid(options.group, key, options.server);
if options.add == True:
	print "Your group id is " + gid + " and your auth key is " + key
	create(gid, options.duration, key, options.server, options.group)
elif options.remove == True:
	mtid = open ('mtid.txt', 'r')
	mid = mtid.read()
	mtid.close()
	print "removing maintenance with id " + mid
	remove(key, mid, options.server)
	os.remove("mtid.txt")
else:
	print "ERROR! Please specify -a to add or -r to remove"
	sys.exit(1)
sys.exit(0)