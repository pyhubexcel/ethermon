#!/bin/bash

GF_UTILS_FILE="/usr/lib64/python2.6/site-packages/gevent_fastcgi/utils.py"
if [ -f $GF_UTILS_FILE ] && grep -q "{}_struct" $GF_UTILS_FILE; then
	echo 'Patch gevent fastcgi lib for Python 2.6'
	sed -i "s/{}_struct/{0}_struct/g" $GF_UTILS_FILE
fi
GF_BASE_FILE="/usr/lib64/python2.?/site-packages/gevent_fastcgi/base.py"
if [ -f $GF_BASE_FILE ] && ! grep -q "readline(" $GF_BASE_FILE ; then
	echo 'Patch gevent fastcgi lib for werkzeug / flask'
	sed -i "s/    def readlines(/    def readline(self, size=-1):\n        self._eof_received.wait()\n        return self._file.readline(size)\n\n    def readlines(/g" $GF_BASE_FILE
fi
