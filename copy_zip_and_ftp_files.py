#Copies files from a bunch of UNC paths, zips them up with the date appended to the file name, then FTPs to a place of your choosing.

#Import necessary stuff
import sys
from shutil import *
import zipfile
import os
import ftplib
from optparse import OptionParser
import time
import socket
from ftplib import FTP_TLS
import logging
import zlib

#set the date to append to filenames.
mydate = time.strftime("%y%m%d", time.localtime())
#LOG_FILENAME = 'c:/temp/web_log.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)


#Copy files from source to dest
def file_copy(source,dest):
    try:
        for each in source:
            print each
            hostdest=each.split("\\")[2]
            newdest = dest + '\\' + hostdest +'\\'
            try:
                print newdest
                os.makedirs(newdest)
            except WindowsError, error:
                copy(each,newdest)
                continue
            copy(each,newdest)
    except WindowsError, error:
        print mydate + 'OS Error Encountered:' + str(error)
	logging.info(mydate+ ' - '+'OS Error Encountered: '+ str(error))
        sys.exit()

def src_file_list(listpath):
    list=[]
    split_items=listpath.split(',')
    for item in split_items:
        for root, dirs, files in os.walk(item,topdown=False):
            for file in files:
                path=os.path.join(root,file)
                list.append(path)
    return list
        
#create a list of files to zip
def dest_file_list(listpath):
    list=[]
    for root, dirs, files in os.walk(listpath,topdown=False):
        for file in files:
            path=os.path.join(root,file)
            list.append(path)
    return list

#zip the files with the date stamp.
def file_zip(list):
    compression=zipfile.ZIP_DEFLATED
    newzip=str(options.zip_dest).split('.')[0]+'-'+mydate+'.zip'
    zip = zipfile.ZipFile(newzip, mode="w", compression=compression, allowZip64=True)
    for each in list:
        zip.write(each)
    zip.close()

#FTP the zip file
def file_ftp(host,un,pw,ftp_filename,source_filename):
    try:
        ftp = ftplib.FTP(host)
        ftp.login(un,pw)
        ftp.storbinary("STOR " + ftp_filename, file(source_filename, "rb"))
        ftp.quit()
    except ftplib.all_errors, error:
        print mydate + 'Error:' + str(error)
        logging.info(mydate+ ' - '+'FTP Error Encountered: '+ str(error))
        sys.exit(0)

#FTPS the zip file
def file_ftps(host,un,pw,ftp_filename,source_filename):
    try:
        ftps = FTP_TLS(host)
        ftps.auth_tls()
        ftps.login(un,pw)
        ftps.prot_p()
        ftps.storbinary("STOR " + ftp_filename, file(source_filename, "rb"))
        ftps.quit()
    except ftplib.all_errors, error:
        print 'Error:', str(error)
        logging.info(mydate+ ' - '+'FTPS Error Encountered: '+ str(error))
        sys.exit(0)

#Back up the zip file
def file_backup(backup_source,backup_dest):
    copy(backup_source,backup_dest)

#clean up redundant files
def file_cleanup(copied_files,zipped_files,source_cleanup):
    try:
        rmtree(copied_files)
        os.remove(zipped_files)
        if source_cleanup=='true':
            for files in src_file_list(str(options.source)):
                os.remove(files)
    except WindowsError, error:
        print 'OS Error Encountered:', str(error)
        logging.info(mydate+ ' - '+'OS Error Encountered: '+ str(error))
        sys.exit()

#Use optParser to create user-friendly options and help    
parser = OptionParser()
parser.set_defaults(protocol='ftp')
parser.add_option("-s", "--source", dest="source", help="source for file copy", metavar="SOURCE")
parser.add_option("-d", "--dest", dest="dest", help="destination for file copy", metavar="DEST")
parser.add_option("-z", "--zipdest", dest="zip_dest", help="full path for output of zip file (including zip file name)", metavar="ZIP_DEST")
parser.add_option("-H", "--ftphost", dest="host", help="FTP Host", metavar="HOST")
parser.add_option("-u", "--user", dest="un", help="FTP Username", metavar="UN")
parser.add_option("-p", "--pass", dest="pw", help="FTP Password", metavar="PW")
parser.add_option("-f", "--filename", dest="ftp_filename", help="filename for FTP site", metavar="FTP_FILENAME")
parser.add_option("-P", "--protocol", dest="protocol", help="Protocol for FTP; use either ftp or ftps", metavar="PROTOCOL")
parser.add_option("-b", "--backup", dest="backup_dest", help="Location to back up zip file prior to FTP", metavar="BACKUP_DEST")
parser.add_option("-c", "--cleanup", dest="cleanup", help="If set script will delete source files", metavar="CLEANUP")
(options, args) = parser.parse_args()

#Create a list to check for required options
myoptions=[str(options.source),str(options.dest),str(options.zip_dest),str(options.host),str(options.un),str(options.pw),str(options.ftp_filename),str(options.backup_dest)]

#Check if required options are set to "none", and if any are missing print help
for opts in myoptions:
        if opts=='None':
            parser.print_help()
            sys.exit()
            
#This is where we call the functions and the magic happens.
newzip=str(options.zip_dest).split('.')[0]+'-'+mydate+'.zip'
shortzip=str(options.ftp_filename).split('.')[0]+'-'+mydate+'.zip'
file_copy(src_file_list(str(options.source)),str(options.dest))
print "Zipping files"
file_zip(dest_file_list(str(options.dest)))
print "backing up"
file_backup(newzip,str(options.backup_dest))
print "Beginning FTP Process"
if str(options.protocol)=='ftp':
    file_ftp(str(options.host),str(options.un),str(options.pw),shortzip,newzip)
elif str(options.protocol)=='ftps':
    file_ftps(str(options.host),str(options.un),str(options.pw),shortzip,newzip)
else:
    print "no protocol given"
print "cleaning up"
file_cleanup(str(options.dest),newzip,str(options.cleanup))
#logfile.close()
