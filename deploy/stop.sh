#!/bin/bash
DIR=`dirname $0`
if [ $# -lt 1 ]
then
	echo "Usage: stop.sh module1 [module2...]"
	exit
fi
for arg in $@
do
	if [ -f "$DIR/$arg/config.sh" ]
	then
		echo "Stopping $arg..."
		. "$DIR/config.sh"
		if [ -f "$DIR/$arg/stop.sh" ]
		then
			/bin/bash "$DIR/$arg/stop.sh"
		else
			. "$DIR/$arg/config.sh"
			if [ -f $FCGI_PID_FILE ]
			then
				pid=`cat $FCGI_PID_FILE`
				echo Detected running $MODULE, PID=$pid
				p=`ps aux|awk '{print $2}'|grep "^$pid$"`
				while [ "$p" ]
				do
					kill "$pid"
					sleep 0.3
					p=`ps aux|awk '{print $2}'|grep "^$pid$"`
				done
					rm -f $FCGI_PID_FILE
				echo "Stopped $MODULE"
			else 
				echo No running $MODULE
			fi	
		fi
	else
		echo "Module $arg to stop not found!"
	fi
done

