#!/bin/bash
DIR=`dirname $0`
. "$DIR/config.sh"

p=`ps ax |grep "$PROJECT/" | grep "$PROCESS_NAME"|grep -v grep|grep -v "\.sh"`
if [ "$p" ]; then
	echo "Before Stop"
	ps ax|grep "$PROJECT/"|grep "$PROCESS_NAME"|grep -v grep|grep -v "\.sh"
	ps ax|grep "$PROJECT/"|grep "$PROCESS_NAME"|grep -v grep|grep -v "\.sh"|awk '{printf("kill -9 %s\n", $1)}'|bash
	echo "Wait Stop..."
	p=`ps ax|grep "$PROJECT/"|grep "$PROCESS_NAME"|grep -v grep|grep -v "\.sh"`
	while [ "$p" ]
	do
		sleep 1
		p=`ps ax|grep "$PROJECT/"|grep "$PROCESS_NAME"|grep -v grep|grep -v "\.sh"`
	done
	echo "After Stop"
	ps ax|grep "$PROJECT/"|grep "$PROCESS_NAME"|grep -v grep|grep -v "\.sh"
	rm -f $FCGI_PID_FILE
else
	echo No running $MODULE
fi