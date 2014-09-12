#!/usr/bin/python

import os
import sys
import csv
from optparse import OptionParser

def csv_report(input_file, output_file):
    #Setup the file / csv reader
    thedata = open(input_file,'rb')
    thereader = csv.reader(thedata, delimiter=',')
    total_lines = len(list(thereader))
    thedata.close()

    mydata = open(input_file,'rb')
    myreader = csv.reader(mydata, delimiter=',')

    myresult = open(output_file, 'a')
    myresult.write(input_file+'\n')

    global_line = 0
    page_count = 0

    last_page = 'last_page'
    page_name = 'page_name'

    val1 = 0
    val2 = 0
    val3 = 0
    val4 = 0
    val5 = 0
    val6 = 0
    val7 = 0

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

        print row
        #Group the shit here on page_name

        if last_page == page_name and global_line == total_lines:
            page_count = page_count+1
            #Add the shit here
            val1 = val1+int(total_time)
            val2 = val2+int(back_end)
            val3 = val3+int(front_end)
            val4 = val4+int(connect_time)
            val5 = val5+int(redirect_time)
            val6 = val6+int(download_time)
            val7 = val7+int(dom_time)

            total_avg = val1 / page_count
            back_avg = val2 / page_count
            front_avg = val3 / page_count
            connect_avg = val4 / page_count
            redirect_avg = val5 / page_count
            download_avg = val6 / page_count
            dom_avg = val7 / page_count

            print "Last Page: "+last_page+" Current Page: "+page_name+' IF count:'+str(page_count)
            print "If Totals: %s, %s, %s, %s, %s, %s, %s" % (total_time, back_end, front_end, connect_time, redirect_time, download_time, dom_time)
            print "If Avgs: %i, %i, %i, %i, %i, %i, %i\n" % (total_avg, back_avg, front_avg, connect_avg, redirect_avg, download_avg, dom_avg)
            myresult.write(last_page+','+flow_name+','+browser+','+str(total_avg)+','+str(back_avg)+','+str(front_avg)+','+str(connect_avg)+','+str(redirect_avg)+','+str(download_avg)+','+str(dom_avg)+'\n')

        elif last_page == page_name:
            page_count = page_count+1
            #Add the shit here
            val1 = val1+int(total_time)
            val2 = val2+int(back_end)
            val3 = val3+int(front_end)
            val4 = val4+int(connect_time)
            val5 = val5+int(redirect_time)
            val6 = val6+int(download_time)
            val7 = val7+int(dom_time)

            #total_avg = val1 / page_count
            #back_avg = val2 / page_count
            #front_avg = val3 / page_count
            #connect_avg = val4 / page_count
            #redirect_avg = val5 / page_count
            #download_avg = val6 / page_count
            #dom_avg = val7 / page_count

            #print "Last Page: "+last_page+" Current Page: "+page_name+' ELIF count:'+str(page_count)
            #print "Elif Totals: %s, %s, %s, %s, %s, %s, %s" % (total_time, back_end, front_end, connect_time, redirect_time, download_time, dom_time)
            #print "Elif Avgs: %i, %i, %i, %i, %i, %i, %i\n" % (total_avg, back_avg, front_avg, connect_avg, redirect_avg, download_avg, dom_avg)

        else:
            if last_page == 'last_page':
                page_count = page_count+1

                #Add the shit here
                val1 = val1+int(total_time)
                val2 = val2+int(back_end)
                val3 = val3+int(front_end)
                val4 = val4+int(connect_time)
                val5 = val5+int(redirect_time)
                val6 = val6+int(download_time)
                val7 = val7+int(dom_time)

                #print "Last Page: "+last_page+" Current Page: "+page_name+' ELSE count:'+str(page_count)
                #print "Else Totals: %s, %s, %s, %s, %s, %s, %s" % (total_time, back_end, front_end, connect_time, redirect_time, download_time, dom_time)
                #print "Else Avgs: %i, %i, %i, %i, %i, %i, %i\n" % (total_avg, back_avg, front_avg, connect_avg, redirect_avg, download_avg, dom_avg)

            else:
                total_avg = val1 / page_count
                back_avg = val2 / page_count
                front_avg = val3 / page_count
                connect_avg = val4 / page_count
                redirect_avg = val5 / page_count
                download_avg = val6 / page_count
                dom_avg = val7 / page_count

                print "Last Page: "+last_page+" Current Page: "+page_name+' ELSE count:'+str(page_count)
                print "Else Totals: %s, %s, %s, %s, %s, %s, %s" % (total_time, back_end, front_end, connect_time, redirect_time, download_time, dom_time)
                print "Else Avgs: %i, %i, %i, %i, %i, %i, %i\n" % (total_avg, back_avg, front_avg, connect_avg, redirect_avg, download_avg, dom_avg)
                myresult.write(last_page+','+flow_name+','+browser+','+str(total_avg)+','+str(back_avg)+','+str(front_avg)+','+str(connect_avg)+','+str(redirect_avg)+','+str(download_avg)+','+str(dom_avg)+'\n')

                val1 = val1+int(total_time)
                val2 = val2+int(back_end)
                val3 = val3+int(front_end)
                val4 = val4+int(connect_time)
                val5 = val5+int(redirect_time)
                val6 = val6+int(download_time)
                val7 = val7+int(dom_time)


                last_page = page_name


            last_page = page_name
            page_count = 0
            #Zero out the shit here
            val1 = 0
            val2 = 0
            val3 = 0
            val4 = 0
            val5 = 0
            val6 = 0
            val7 = 0

    mydata.close()
    myresult.write('\n')
    myresult.close()


parser = OptionParser()
parser.add_option("-i", "--input", dest="input", help="Input file to compute (Cannot be used with recursive option)", metavar="IFILE")
parser.add_option("-o", "--output", dest="output", help="Output file to compute (Cannot be used with recursive option)", metavar="OFILE")
parser.add_option("-r", "--recursive", dest="path", help="Recurse through specified path (Cannot be used with file option)", metavar="PATH")
(options, args) = parser.parse_args()

if str(options.path) == 'None':
    csv_report(options.input,options.output)

else:
    searchpath = options.path
    for root, dir, file in os.walk(searchpath,topdown=False):
        for name in file:
            path = os.path.join(root,name)
            csv_report(path,options.output)
