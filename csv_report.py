#!/usr/bin/python

import os
import csv

#Setup the file / csv reader
thedata = open('raw_data.csv','rb')
thereader = csv.reader(thedata, delimiter=',')
total_lines = len(list(thereader))
thedata.close()
mydata = open('raw_data.csv','rb')
myreader = csv.reader(mydata, delimiter=',')
global_line = 0
page_count = 1
last_page = 'last_page'
page_name = 'page_name'

for row in myreader:

    global_line = global_line+1

    #LABEL THE SHIT HERE
    page_name = row[0]
    flow_name = row[1]
    browser = row[2]
    total_time = row[3]
    back_end = row[4]
    front_end = row[5]
    connect_time = row[6]
    redirect_time = row[7]
    download_time = row[8]
    dom_time = row[9]

    #Group the shit here on page_name
    if last_page == page_name and global_line == total_lines:
        page_count = page_count+1
        print last_page+' count:'+str(page_count)
        #print "If Loop - "+last_page+" "+page_name
    elif last_page == page_name:
        #print "Elif Loop One - "+last_page+" "+page_name
        page_count = page_count+1
    #elif last_page == 'last_page':
    #    #print "Elif Loop Two - "+last_page+" "+page_name
    else:
        #print "Else Loop - "+last_page+" "+page_name
        print last_page+' count:'+str(page_count)
        last_page = page_name
        page_count = 1
    #print global_line

mydata.close()
