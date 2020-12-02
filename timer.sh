#!/bin/bash
#
# Author:  Dlo Bagari
# created Date: 12-18-2019
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
while true
do
IS_OKTA_CASB=$(systemctl is-active okta_casb.service)
if [[ "$IS_OKTA_CASB" == "active" ]];then
  sleep 5
else
  # find the sleep time between each risk level download
  SLEEP_TIME=$(cat ${DIR}/settings.yml | grep 'interval_time' | awk -F':' '{print $2}' | sed 's/^[ \t]*//;s/[ \t]*$//')
  a=$(( $SLEEP_TIME * 60 ))
  sleep ${a}
  systemctl restart okta_casb.service
fi
done