#!/usr/bin/env python
# <*******************
# 
# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the parties, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# 
# *******************>

from urlparse import urlparse


def validateParalellProcessNumber(string_parallelProcesses):
    try:
        nr= int(string_parallelProcesses)
        if nr < 0 or nr > 25 :
            return False
        return True
    except:
        return False

def validatePort(string_port):
    try:
        port= int(string_port)
        if port < 0 or port > 65534 :
            return False
        return True
    except:
        return False

def validateUrl(string_url):
    try:
         urlparse(string_url)
         return True
    except:
        return False
