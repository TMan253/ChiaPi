#!/bin/bash

# Define Chia blockchain install path:
CB_DIR="/home/chia/chia-blockchain/"
cd "${CB_DIR}"
. ./activate

# Define Chia blockchain log file:
LOG_FILE="/chia/logs/farmer.$(date '+%Y-%m-%d').log"

# Check for already-running farmer instances.
PID_COUNT=$( ps -ef | grep -v grep | grep chia_ | wc -l )

# Bail out if any farmer instances are already running.
if [ 0 -ne $PID_COUNT ]
then
  exit
fi

# If no farmer instances are running, then start one.
echo "$( date "+%Y-%m-%d-%H:%M:%S.%N" ) - Starting Chia farmer." | tee -a "${LOG_FILE}"
chia start farmer-only harvester >> "${LOG_FILE}" 2>&1 &


