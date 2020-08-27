#!/bin/bash
dir=`dirname $0`
if [ $# -lt 1 ]
then
	echo "usage: $0 DIRECTORY [DELETE_DAYS] [COMPRESS_DAYS] [COMPRESS_FILE_PATTERN] [DATE_PATTERN]"
	echo "multiple matches example for COMPRESS_FILE_PATTERN: data|error"
	exit
fi
path=$1
if [ $# -gt 1 ]
then
	log_delete_days=$2
else
	log_delete_days=7
fi
if [ $# -gt 2 ]
then
	log_compress_days=$3
else
	log_compress_days=0
fi
if [ $# -gt 3 ]
then
	log_compress_match=$4
else
	log_compress_match='*'
fi
if [ $# -gt 4 ]
then
	date_pattern=$5
else
	date_pattern="%Y-%m-%d"
fi
if [ $log_delete_days -gt 0 ]
then
	files=`ls $path/*.log.*`
	i=0
	while [ $i -le $log_delete_days ]
	do
		d=`date "+$date_pattern" --date "$i day ago"`
		files=`echo "$files"|grep -v $d`
		i=`expr $i + 1`
	done
	echo "$files"|xargs rm -f
fi
if [ $log_compress_days -gt 0 ] && [ -n "$log_compress_match" ]
then
	files=`ls $path/*.log.*|grep -v "\.gz$"|grep -E "$log_compress_match"`
	i=0
	while [ $i -lt $log_compress_days ]
	do
		d=`date "+$date_pattern" --date "$i day ago"`
		files=`echo "$files"|grep -v $d`
		i=`expr $i + 1`
	done
	echo "$files"|xargs gzip
fi
