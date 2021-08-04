#!/bin/sh
source /etc/profile

echo "stop server..."
cd /data/server/Saturn
pidlist=`ps -ef |grep saturn.py | awk '{print $2}'`
kill -9 $pidlist

pidlist=`ps -ef |grep multiprocessing | awk '{print $2}'`
kill -9 $pidlist

echo "delete temp file success..."
nohup python3 saturn.py &
echo "start server..."
sleep 15
