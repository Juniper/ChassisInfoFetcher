#!/usr/bin/env bash

apt-get update
sudo apt-get install -y python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev git
sudo apt-get --no-install-recommends install virtualbox-guest-utils
sudo apt-get install python-paramiko
sudo pip install --upgrade setuptools
sudo pip install --upgrade junos-eznc
sudo pip install urwid
sudo pip install enum
git clone https://github.com/Juniper/py-space-platform.git
sudo pip install ./py-space-platform
