#!/usr/bin/env bash

apt-get update
sudo apt-get install -y python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev git
sudo apt-get --no-install-recommends install virtualbox-guest-utils
sudo pip install --upgrade pip
sudo pip install junos-eznc
sudo pip install urwid
git clone https://github.com/Juniper/py-space-platform.git
sudo pip install ./py-space-platform
