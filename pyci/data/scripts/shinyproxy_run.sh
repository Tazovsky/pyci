#!/bin/bash -e

PATH_TO_JAR=$1
PID_FILE=$2

[ -z "$PATH_TO_JAR" ] && echo "PATH_TO_JAR is not provided" && exit 1
[ -z "$PID_FILE" ] && echo "PID_FILE is not provided" && exit 1

echo ">>>>> run"
exit 0

if [ -f $PID_FILE ]; then
    PID=$(cat $PID_FILE)
    echo "Killing Process ID: $PID..."
    kill $PID
    rm -f $PID_FILE
fi

nohup java -jar $PATH_TO_JAR
echo $! > $PID_FILE