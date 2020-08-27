#!/bin/bash
DIR=`dirname $0`
if [ $# -lt 1 ]
then
	echo "Usage: start.sh module1 [module2...]"
	exit
fi
. "$DIR/config.sh"
WORK_DIR=`readlink -f $CURRENT_DIR`
for arg in $@
do
	if [ -f "$DIR/$arg/config.sh" ]
	then
		echo "Starting $arg..."
		/bin/bash $DIR/stop.sh $arg
		. "$DIR/config.sh"
		if [ -f "$DIR/$arg/start.sh" ]
		then
			/bin/bash "$DIR/$arg/start.sh"
		else
			. "$DIR/$arg/config.sh"
			python $WORK_DIR/common/fastcgi.py	\
				:$FCGI_PORT	\
				--work-dir $WORK_DIR	\
				--wsgi $MODULE.wsgi:application	\
				--max-conns $FCGI_MAX_CONNS	\
				--num-workers $FCGI_WORKERS	\
				--buffer-size $FCGI_BUFFER_SIZE	\
				--daemon $FCGI_PID_FILE	\
				--stdout $ROOT_DIR/log/$MODULE/daemon.log
			echo Started $MODULE, PID=`cat $FCGI_PID_FILE`
		fi
	else
		echo "Module $arg not found!"
	fi
done

