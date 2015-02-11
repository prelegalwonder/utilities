#!/bin/bash

show_help() {
   cat << EOF
   Usage: ${0##*/} [-hv] [-t TYPE] ...
   Do stuff with FILE and write the result to standard output. With no FILE
   or when FILE is -, read standard input.
   
       -h          display this help and exit
       -t TYPE     Backup type, full or incremental (full | inc)
EOF
}

prereqs() {
    /bin/systemctl status mysql.service | grep running &> /dev/null
    if [ $? -ne 0 ]
      then
      echo 'MySQL service needs to be running before taking backup.'
      exit
    fi

    if [ ! -d "$inc_dir" ] 
      then
      echo "Incremental directory $inc_dir doesn't exist, creating it."
      mkdir -p $inc_dir
    fi

    if [ ! -d "$full_dir" ]
      then
      echo "Full directory $full_dir doesn't exist, creating it."
      mkdir -p $full_dir
    fi
    
}

rollup() {
  last_full=$1
  last_inc=$2
  innobackupex --user=$myuser --apply-log --redo-only $full_dir/$last_full >> $backup_log 2>&1
  if [ $? -eq 0 ] #003
    then
    for dir in `ls -ltr $inc_dir | awk '{print $9}'`
      do
      echo -n "."
      innobackupex --user=$myuser --apply-log --redo-only $full_dir/$last_full --incremental-dir=$inc_dir/$dir >> $backup_log 2>&1
      if [ $? -ne 0 ] #001
        then
        echo "Incremental prepare failed on $inc_dir/$dir, aborting roll-up and removing previous incrementals."
        rm -rf $full_dir/$last_full 
        rm -rf $inc_dir/*
        break
      else
        continue
      fi #001
    done
    innobackupex --user=$myuser --apply-log $full_dir/$last_full >> $backup_log 2>&1
    if [ $? -ne 0 ] #002
      then
      echo "Final prepare failed on $full_dir/$last_full, aborting roll-up and removing previous full and incrementals."
      rm -rf $full_dir/$last_full 
      rm -rf $inc_dir/*
    else
      echo -e "\nFinal prepare on $full_dir/$last_full succeeded, removing previous incrementals."
      rm -rf $inc_dir/*
    fi #002
    rm $full_dir/backup.lock
  fi #003
}
    

backup() {
  last_full=`ls -lrt $full_dir | awk '{ print $9 }' | tail -1`
  last_inc=`ls -lrt $inc_dir | awk '{ print $9 }' | tail -1`

  if [ $btype == 'full' ] #006
    then
    touch $full_dir/backup.lock
    echo "Performing full backup into $full_dir.."
    innobackupex --user=$myuser $full_dir &> $backup_log
    if [ $? -eq 0 ] #005
      then
      new_last=`ls -ltr $full_dir | awk '{ print $9 }' | tail -1`
      echo "New full-backup successful. Rolling previous incrementals into previous full backup."
      rollup $last_full $last_inc
    else
      echo "Full backup failed. See backup log $backup_log"
    fi
    touch $full_dir/$new_last
  elif [ $btype == 'inc' ]
    then
    touch $full_dir/backup.lock
    if [ `echo $last_inc | wc -c` -lt 20 ] #004 
      then
      echo "Creating incremental backup with $full_dir/$last_full as base.."
      innobackupex --user=$myuser --incremental $inc_dir --incremental-basedir $full_dir/$last_full &> $backup_log
    elif [ `echo $last_inc | wc -c` -gt 20 ]
      then
      echo 'Something went wrong getting the last incremental directory'
      exit
    else 
      echo "Creating incremental backup with $inc_dir/$last_inc as base.."
      innobackupex --user=$myuser --incremental $inc_dir --incremental-basedir $inc_dir/$last_inc &> $backup_log
    fi #004
    rm $full_dir/backup.lock
  else
    echo 'No backup type specified.'
  fi #005
}

while getopts "h?:l:t:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    v)  verbose=1
        ;;
    t)  btype=`echo $OPTARG | awk '{print tolower($0)}'`
        ;;
    l)  log_path=$OPTARG
        ;;
    esac
done

myuser=areplogle
full_dir=/opt/mysqlback/backups/full
inc_dir=/opt/mysqlback/backups/inc
backup_log=/opt/mysqlback/logs/backup.log

if [ -f "$full_dir/backup.lock" ]
  then
  echo "Other work in progress. $full_dir/backup.lock exists"
  exit
fi

prereqs
backup
