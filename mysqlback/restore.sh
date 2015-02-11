#!/bin/bash

show_help() {
   cat << EOF
   Usage: ${0##*/} [-hv] [-t TYPE] ...
   Do stuff with FILE and write the result to standard output. With no FILE
   or when FILE is -, read standard input.
   
       -h          display this help and exit
       -t TYPE     Restore type, full or incremental (full | inc)
EOF
}

prereqs() {
    /bin/systemctl status mysql.service | grep inactive &> /dev/null
    if [ $? -ne 0 ]
      then
      echo 'MySQL service needs to be stopped before restoring a backup.'
      exit
    fi

    if [ ! -d "$inc_dir" ] 
      then
      echo "Incremental directory $inc_dir doesn't exist, ensure you've specified the correct directory."
      exit
    fi

    if [ ! -d "$full_dir" ]
      then
      echo "Full directory $full_dir doesn't exist, ensure you've specified the correct directory."
      exit
    fi
    
}
    
prepare() {
    last_full=`ls -lrt $full_dir | awk '{ print $9 }' | tail -1`
    touch $full_dir/backup.lock
    echo "Preparing backup.."
    if [ $rtype == 'inc' ]
      then
      echo "Preparing initial on $full_dir/$last_full .." 
      innobackupex --user=$myuser --apply-log --redo-only $full_dir/$last_full &> $restore_log
      if [ $? -eq 0 ]
        then
        for dir in `ls -ltr $inc_dir | awk '{print $9}'`
          do
	  echo "Preparing $inc_dir/$dir .."
          innobackupex --user=$myuser --apply-log --redo-only $full_dir/$last_full --incremental-dir=$inc_dir/$dir >> $restore_log 2>&1
          if [ $? -ne 0 ]
            then
            echo "Incremental prepare failed on $inc_dir/$dir"
            exit
          else
            continue
          fi
        done
        echo "Preparing final on $full_dir/$last_full .."
        innobackupex --user=$myuser --apply-log $full_dir/$last_full >> $restore_log 2>&1
        if [ $? -ne 0 ]
          then
          echo "Final prepare of full backup failed."
          exit
        else
	  echo "Final prepare of full backup succeeded, removing all incrementals that have been rolled-up into $full_dir/$last_full"
          rm -rf $inc_dir/*
	fi
      else
        echo "Initial apply to full backup failed."
      fi
    elif [ $rtype == 'full' ]
      then
      echo "Preparing $full_dir/$last_full .."
      innobackupex --user=$myuser --apply-log $full_dir/$last_full &> $restore_log
      if [ $? -ne 0 ]
        then
        echo "Final prepare of full backup failed."
        exit
      fi
    else
      echo "No restore type provided. Exiting."
      exit
    fi
    echo "Prepare stage completed."
}

restore() {
    last_full=`ls -lrt $full_dir | awk '{ print $9 }' | tail -1`
    cd $full_dir/$last_full
    echo "Restoring backup staged in $last_full"
    rsync -rvt --exclude 'xtrabackup_checkpoints' --exclude 'xtrabackup_logfile' ./ /var/lib/mysql >> $restore_log 2>&1
    echo "Setting correct permissions."
    chown -R mysql.mysql /var/lib/mysql
    echo "Restore Completed."
    rm $full_dir/backup.lock
}

while getopts "h?:l:t:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1V
        ;;
    t)  rtype=`echo $OPTARG | awk '{print tolower($0)}'`
        ;;
    l)  log_path=$OPTARG
        ;;
    esac
done

myuser=areplogle
full_dir=/opt/mysqlback/backups/full
inc_dir=/opt/mysqlback/backups/inc
restore_log=/opt/mysqlback/logs/restore.log

if [ -f "$full_dir/backup.lock" ]
  then
  echo "Other work in progress. $full_dir/backup.lock exists"
  exit
fi

prereqs
prepare
restore
