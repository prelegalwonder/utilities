#!/usr/bin/python

import os,sys
import json,string
import time
import datetime

#System call to get snapshot info and prep it for json
myss = os.popen('sudo convoy list','r')
myssout = myss.read()
myssjson = json.loads(myssout)

#System call to get backup info and prep it for json
bupath = 'vfs:///mnt/nfs/c7engs004/Backup/docker/convoy'
mybu = os.popen('sudo convoy backup list '+bupath,'r')
mybuout = mybu.read()
mybujson = json.loads(mybuout)

#iterate through syscall output building a dictionary of snapshots with
#needed info and convert ISO dates to epoch for easier eval.
def listSnapshots(convoyPayload):
    pattern = '%a %b %d %H:%M:%S -0500 %Y'
    result = {}
    for k1, v1 in convoyPayload.iteritems():
        if v1["Snapshots"]:
            ssparent = v1["Name"]
            for k2, v2 in v1["Snapshots"].iteritems():
                ssuuid = str(v2["UUID"])
                ssname = str(v2["Name"])
                ssepoch = int(time.mktime(time.strptime(str(v2["CreatedTime"]), pattern)))
                result[ssname] = [ssepoch, ssuuid, ssparent]
    return result

def listBackups(convoyPayload):
    pattern = '%a %b %d %H:%M:%S -0500 %Y'
    result = {}
    for k1, v1 in convoyPayload.iteritems():
	buname = v1["SnapshotName"] 
	bufurl = v1["BackupURL"]
        buepoch = int(time.mktime(time.strptime(str(v1["CreatedTime"]), pattern)))
        result[buname] = [buepoch, bufurl]
    return result

#take user defined criteria to filter select snapshots
def selectSnapshots(snapshots,criteria):
    pattern = '%Y-%m-%d'
    filterResult=[]
    if criteria[1] == "older":
        beforeDatePre = datetime.date.today() - datetime.timedelta(days=int(criteria[2]))
        beforeDatePost = int(time.mktime(time.strptime(str(beforeDatePre), pattern)))
        for snapshot, data in snapshots.iteritems():
            if int(data[0]) <= beforeDatePost:
                filterResult.append(snapshot)
    elif criteria[1] == "newer":
        afterDatePre = criteria[2]
        afterDatePost = int(time.mktime(time.strptime(str(afterDatePre), pattern)))
        for snapshot, data in snapshots.iteritems():
            if int(data[0]) >= afterDatePost:
                filterResult.append(snapshot)
    elif criteria[1] == "like":
        import  re
        for snapshot, data in snapshots.iteritems():
            mysearch = re.search(criteria[2], snapshot, re.M|re.I)
            if mysearch:
                filterResult.append(snapshot)
    elif criteria[1] == "parent":
        for snapshot, data in snapshots.iteritems():
            if criteria[2] == data[2]:
                filterResult.append(snapshot)
    return filterResult

def selectBackups(backups,criteria):
    pattern = '%Y-%m-%d'
    filterResult=[]
    if criteria[1] == "older":
        beforeDatePre = datetime.date.today() - datetime.timedelta(days=int(criteria[2]))
        beforeDatePost = int(time.mktime(time.strptime(str(beforeDatePre), pattern)))
        for backup, data in backups.iteritems():
            if int(data[0]) <= beforeDatePost:
                filterResult.append([backup,data[1]])
    elif criteria[1] == "newer":
        afterDatePre = criteria[2]
        afterDatePost = int(time.mktime(time.strptime(str(afterDatePre), pattern)))
        for backup, data in backups.iteritems():
            if int(data[0]) >= afterDatePost:
                filterResult.append([backup,data[1]])
    elif criteria[1] == "like":
        import  re
        for backup, data in backups.iteritems():
            mysearch = re.search(criteria[2], backup, re.M|re.I)
            if mysearch:
                filterResult.append([backup,data[1]])
    return filterResult

def delSnapshots(snapshots):
    for snapshot in snapshots:
        mydelete = os.popen("sudo convoy snapshot delete "+snapshot,'r')
        if mydelete.close() is not None:
            print "Removal of "+snapshot+" failed: "+mydelete.read()
        else:
            print "Removed: "+snapshot

def delBackups(backups):
    for backup in backups:
	bupath = backup[1].rstrip('\n')
        mydelete = os.popen("sudo convoy backup delete '"+bupath+"'",'r')
        if mydelete.close() is not None:
            print "Removal of "+backup[0]+" failed: "+mydelete.read()
        else:
            print "Removed: "+backup[0]

def showSnapshots(snapshots):
    print "Snapshots: "
    for snapshot in snapshots:
        print "            "+snapshot

def showBackups(backups):
    print "Backups: "
    for backup in backups:
        print "            "+backup[0]+" : "+str(backup[1]) 


snapshots = listSnapshots(myssjson)
backups = listBackups(mybujson)

if sys.argv[1] == "delete":
    delSnapshots(selectSnapshots(snapshots,[sys.argv[1],sys.argv[2],sys.argv[3]]))
    delBackups(selectBackups(backups,[sys.argv[1],sys.argv[2],sys.argv[3]]))
elif sys.argv[1] == "show":
    showSnapshots(selectSnapshots(snapshots,[sys.argv[1],sys.argv[2],sys.argv[3]]))
    showBackups(selectBackups(backups,[sys.argv[1],sys.argv[2],sys.argv[3]]))


