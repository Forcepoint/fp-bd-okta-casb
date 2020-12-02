#!/usr/bin/env bash
# check if settings file is exists
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo " install Requirements"
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
sudo yum install -y python36u python36u-libs python36u-devel python36u-pip
sudo pip3 install PyYAML
sudo pip3 install requests

SETTINGS_FILE=${DIR}/settings.yml

if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo "The settings file:$SETTINGS_FILE does not exist"
    exit 1
fi
echo "Moving files to application directory"
APPLICATION_DIRECTORY="$(python3 "$DIR"/scripts/installer_helper.py "$SETTINGS_FILE")"
cp -rf ./* ${APPLICATION_DIRECTORY}
chmod +x ${APPLICATION_DIRECTORY}/riskscore.sh
chmod +x ${APPLICATION_DIRECTORY}/timer.sh
${APPLICATION_DIRECTORY}/riskscore.sh service -c ${APPLICATION_DIRECTORY}/settings.yml

systemctl enable okta_casb.service
systemctl enable okta_casb_timer.service
sleep 4
rm -rf ${DIR}/* 2> /dev/null