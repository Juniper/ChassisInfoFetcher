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

from __future__ import print_function
import base64
import os
import socket
import sys
import time
import traceback
import string
import re
import json

from multiprocessing import Pool
from datetime import date, datetime, timedelta

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.exception import *
from lxml import etree
from directFetcher import DirectFetcher

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)    


import logging
import logging.config

TIMEOUT_REST_API = 3

class AssistedFetcher(DirectFetcher):

   
     
    # Override the load and validate to work from Junos Space instead of intput file
    # return (False,ErrorMessage) if inputs are invalid or (True,SuccessMessage) if they are valid
    def LoadInputFile(self):
        
        devices= []
        general_settings= []

        #### Read the general settings information
        try:
            with open('conf/assistedFetcher.conf') as data_file:    
                general_settings = json.load(data_file)
        except:
            msg="Loading and Verifying Device List : Unable to read input or parse file 'assistedFetcher.conf' responsible for storing general settings."
            logging.error(msg)
            return (False,msg)
        
        self.THREADCOUNT=int(general_settings["parallelProcesses"])
        
        ### Prepare call to the Junos Space REST API
        url="https://%s/api/space/device-management/devices"%(general_settings["url"])
        auth=HTTPBasicAuth(general_settings["js_username"] , general_settings["js_password"])
        headers = {'accept':'application/vnd.net.juniper.space.device-management.devices+json;version=1'}
        payload=""
        
        try:
            response = requests.get(url,verify=False,data=payload,headers=headers,auth=auth,timeout=TIMEOUT_REST_API)
        except:
            msg="Loading and Verifying Device List : Unable to retrive the device list from Junos Space."
            logging.error(msg)
            return (False,msg)
        
        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg="Loading and Verifying Device List : The device list from Junos Space is empty."
            logging.error(msg)
            return (False,msg)
          
        try:  
            result=json.loads(response.text)
        except:
            msg="Unable to interpret the json file response.\n       Junos Space response is the following :\n       "+response.text
            logging.error(msg)
            return (False,msg)
                
                 
        #### Build the in-memory structure
        for device in result["devices"]["device"]:
            host_entry={}
         
            for port in general_settings["port"]:
                host_entry["host"]=device["ipAddr"]
                host_entry["username"]=general_settings["device_ssh_username"]
                host_entry["password"]=general_settings["device_ssh_password"]
                host_entry["port"]=port
                self.jobList.append((host_entry))
            
        #print(self.jobList)
        msg="Loading and Verifying Device List : Successful, loaded (%s) hosts!"%str(len(self.jobList))
        logging.info(msg)
        return (True,msg)

   

if __name__ == '__main__':
    logging.config.fileConfig('conf/logging.conf')
    f=AssistedFetcher(sys.argv[1])
    logging.info(f.LoadInputFile())
    #df.job("{'username': 'mkim', 'host': '172.30.77.181', 'password': 'mkim', 'port': '22'}")
    f.Run()
    #df.Run()







