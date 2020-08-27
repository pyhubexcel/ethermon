#!/bin/bash
DIR=`dirname $0`
. "$DIR/config.sh"

echo "Starting $MODULE server..."
python "$SERVER_PATH" start --pid "$FCGI_PID_FILE" --stdout "$DAEMON_LOG_FILE"
echo Started, PID=`cat $FCGI_PID_FILE`
