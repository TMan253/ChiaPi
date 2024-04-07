#!/bin/bash

# Define Chia blockchain install path:
CB_DIR="/home/chia/chia-blockchain/"
cd "${CB_DIR}"
. ./activate

# Define Chia blockchain log file:
LOG_FILE="/chia/logs/farmer-$(date '+%Y-%m-%d').log"

# Check for already-running farmer instances.
PID_COUNT=$( ps -ef | grep -v grep | grep chia_ | wc -l )

# Kill the running daemon instances.
if [ "${PID_COUNT}" != "0" ]
then
  echo "Shutting down Chia daemons."
  chia stop all -d
  for J in {1..30}
  do
    PID_COUNT=$( ps -ef | grep -v grep | grep chia_ | wc -l )
    if [ 0 -eq $PID_COUNT ]
    then
      echo "Chia daemon shutdown complete."
      break
    else
      echo "Waiting for PIDs to quit..."
      sleep 1
    fi
  done
  PID_COUNT=$( ps -ef | grep -v grep | grep chia_ | wc -l )
  if [ "${PID_COUNT}" != "0" ]
  then
    echo -e "Error killing Chia daemons.\nQuitting."
    exit
  fi
fi

# If no farmer instances are running, then start one.
echo "$( date "+%Y-%m-%d-%H:%M:%S.%N" ) - Starting Chia farmer." | tee -a "${LOG_FILE}"
chia start farmer-only harvester >> "${LOG_FILE}" 2>&1 &


