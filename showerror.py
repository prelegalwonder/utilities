#!/cygdrive/c/Python27/python.exe
#Written by Mandrew Sexlogle

import os
import string
import sys
import re
from optparse import OptionParser


def getTerminalSize():
   import platform
   current_os = platform.system()
   tuple_xy=None
   if current_os == 'Windows':
       tuple_xy = _getTerminalSize_windows()
       if tuple_xy is None:
          tuple_xy = _getTerminalSize_tput()
          # needed for window's python in cygwin's xterm!
   if current_os == 'Linux' or current_os == 'Darwin' or  current_os.startswith('CYGWIN'):
       tuple_xy = _getTerminalSize_linux()
   if tuple_xy is None:
       print "default"
       tuple_xy = (80, 25)      # default value
   return tuple_xy

def _getTerminalSize_windows():
    res=None
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except:
        return None
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def _getTerminalSize_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
       import subprocess
       proc=subprocess.Popen(["tput", "cols"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       cols=int(output[0])
       proc=subprocess.Popen(["tput", "lines"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       rows=int(output[0])
       return (cols,rows)
    except:
       return None


def _getTerminalSize_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])


def findError(logfile):
    templist = []
    error = ''
    ts = getTerminalSize()[0]

    for line in logfile:
        templist.append(line)

    for element in templist:
        newlist = element.split(' ')
        if newlist[0] == 'ERROR':
	        error = error+element
        elif re.compile("	at").search(element):
	        error = error+element
        elif re.compile("([A-Za-z]{3,90}\.){3,12}").match(element):
            error = error+element
        elif re.compile("Exception").search(element):
            error = error+element
        elif re.compile("Caught").search(element):
            error = error+element
        elif re.compile("Wrapped").match(element):
            error = error+element
        else:
            if error == '':
                continue
            elif str(options.path) != 'None':
                if str(options.keyword) != 'None':
                    searchError(error,1)
                elif str(options.ignore) != 'None':
                    count = 0
                    ignoreError(error,ts,count)
                else:
                    print path
                    newline = '\n\n\n'
                    print error+newline
            else:
                if str(options.keyword) != 'None':
                    searchError(error,0)
                elif str(options.ignore) != 'None':
                    count = 0
                    ignoreError(error,ts,count)
                else:
                    newline = '\n\n\n'
                    print error+newline
            error = ''

def searchError(Error,PrintPath):
    if re.compile(options.keyword).search(Error) and PrintPath == 1:
        print path
        print Error
    elif re.compile(options.keyword).search(Error):
        print Error	

def ignoreError(Error,ts,count):
    if re.compile(options.ignore).search(Error): 
        div = int(ts)/2
        if count < div:
            sys.stdout.write('.')
        else:
            sys.stdout.write('.\n')


parser = OptionParser()
parser.add_option("-f", "--file", dest="file", help="File to search for errors (Cannot be used with recursive option)", metavar="FILE")
parser.add_option("-r", "--recursive", dest="path", help="Recurse through specified path (Cannot be used with file option)", metavar="PATH")
parser.add_option("-s", "--search", dest="keyword", help="Search for keyword in error", metavar="KEYWORD")
parser.add_option("-i", "--ignore", dest="ignore", help="Ignore any error containing keyword.", metavar="IGNORE")
(options, args) = parser.parse_args()
    

if str(options.path) == 'None':
    logfile = open(options.file,'r')
    findError(logfile)
    logfile.close()

else:
    searchpath = options.path
    for root, dir, file in os.walk(searchpath,topdown=False):
        for name in file:
            path = os.path.join(root,name)
	    logfile = open(path,'r')
            findError(logfile)
	    logfile.close()
    
