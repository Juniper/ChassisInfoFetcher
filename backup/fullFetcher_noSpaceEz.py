#!/usr/bin/env python
"""
 ******************************************************************************
 * Copyright (c) 2014  Juniper Networks. All Rights Reserved.
 *
 * YOU MUST ACCEPT THE TERMS OF THIS DISCLAIMER TO USE THIS SOFTWARE
 *
 * JUNIPER IS WILLING TO MAKE THE INCLUDED SCRIPTING SOFTWARE AVAILABLE TO YOU
 * ONLY UPON THE CONDITION THAT YOU ACCEPT ALL OF THE TERMS CONTAINED IN THIS
 * DISCLAIMER. PLEASE READ THE TERMS AND CONDITIONS OF THIS DISCLAIMER
 * CAREFULLY.
 *
 * THE SOFTWARE CONTAINED IN THIS FILE IS PROVIDED "AS IS." JUNIPER MAKES NO
 * WARRANTIES OF ANY KIND WHATSOEVER WITH RESPECT TO SOFTWARE. ALL EXPRESS OR
 * IMPLIED CONDITIONS, REPRESENTATIONS AND WARRANTIES, INCLUDING ANY WARRANTY
 * OF NON-INFRINGEMENT OR WARRANTY OF MERCHANTABILITY OR FITNESS FOR A
 * PARTICULAR PURPOSE, ARE HEREBY DISCLAIMED AND EXCLUDED TO THE EXTENT ALLOWED
 * BY APPLICABLE LAW.
 * 
 * IN NO EVENT WILL JUNIPER BE LIABLE FOR ANY LOST REVENUE, PROFIT OR DATA, OR
 * FOR DIRECT, SPECIAL, INDIRECT, CONSEQUENTIAL, INCIDENTAL OR PUNITIVE DAMAGES
 * HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY ARISING OUT OF THE
 * USE OF OR INABILITY TO USE THE SOFTWARE, EVEN IF JUNIPER HAS BEEN ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGES.
 * 
 ********************************************************************************
 * Project GIT  :  https://git.juniper.net/asmeureanu/ChassisInfoFetcher
 ********************************************************************************
"""

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




TIMEOUT_REST_API = 3

class FullFetcher(DirectFetcher):
     
    # Override the load and validate to work from Junos Space instead of intput file
    # return (False,ErrorMessage) if inputs are invalid or (True,SuccessMessage) if they are valid
    def LoadInputFile(self):
        
        devices= []
        general_settings= []

        #### Read the general settings information
        try:
            with open('assistedFetcher.conf') as data_file:    
                general_settings = json.load(data_file)
        except:
            return (False,"Loading and Verifying Device List .............  Unable to read input or parse file 'assistedFetcher.conf' responsible for storing general settings.")
        
        self.THREADCOUNT=int(general_settings["parallelProcesses"])
        
        ### Prepare call to the Junos Space REST API
        url="https://%s/api/space/device-management/devices"%(general_settings["url"])
        auth=HTTPBasicAuth(general_settings["username_js"] , general_settings["password_js"])
        headers = {'accept':'application/vnd.net.juniper.space.device-management.devices+json;version=1'}
        payload=""
        
        try:
            response = requests.get(url,verify=False,data=payload,headers=headers,auth=auth,timeout=TIMEOUT_REST_API)
        except:
            return (False,"Loading and Verifying Device List .............  Unable to retrive the device list from Junos Space.")
        
        ### Treat an empty reply as a error
        if response.status_code == 204:
            return (False,"Loading and Verifying Device List .............  The device list from Junos Space is empty.")
          
        result=json.loads(response.text)
        
                 
        #### Build the in-memory structure
        for device in result["devices"]["device"]:
            host_entry={}
            #print (device)
            for port in general_settings["port"]:
                host_entry["host"]=device["ipAddr"]
                host_entry["uri"]=device["@uri"]
                host_entry["url"]=general_settings["url"]
                host_entry["username"]=general_settings["username_js"]
                host_entry["password"]=general_settings["password_js"]
                host_entry["port"]=port
                self.jobList.append(str(host_entry))
            
        #print(self.jobList)
        return (True,"Loading and Verifying Device List .............  Successful, loaded (%s) hosts!"%str(len(self.jobList)))

     # process job 
    def job(self,args):
       
        output=""
        args=eval(args)
        print("Connecting to: "+args["host"])
        print(args)
        
        ### Prepare call to the Junos Space REST API  |  Schedule the job to execute the RPC data
        url="https://%s%s/exec-rpc"%(args["url"],args["uri"])
        auth=HTTPBasicAuth(args["username"] , args["password"])
        headers = {
                'accept':'application/vnd.net.juniper.space.device-management.rpc+json;version=3 ',
                'content-type':'application/vnd.net.juniper.space.device-management.rpc+xml;version=3;charset=UTF-8'
                    }
        payload="""<netconf> 
  <rpcCommands>
    <rpcCommand>
      <![CDATA[<get-system-information/>]]>
    </rpcCommand>
  </rpcCommands>
</netconf>"""
        
        #try:
        response = requests.post(url,verify=False,data=payload,headers=headers,auth=auth,timeout=TIMEOUT_REST_API)
        #except:
        #    return (False,"Loading and Verifying Device List .............  Unable to retrive the device list from Junos Space.")
        #jobUrl = 


        """
        ### Query the job status / retrive the restult
        url="https://%s%s/exec-rpc"%(args["url"],args["uri"])
        auth=HTTPBasicAuth(args["username"] , args["password"])
        headers = {
                'accept':'application/vnd.net.juniper.space.device-management.rpc+xml;version=3 ',
                'content-type':'application/vnd.net.juniper.space.device-management.rpc+xml;version=3;charset=UTF-8'
                    }
        payload=""
        """


        print(response.text)

        print ("Done ["+args["host"]+"].") 
        return output

if __name__ == '__main__':
    f=FullFetcher()
    print(f.LoadInputFile())
    #df.job("{'username': 'mkim', 'host': '172.30.77.181', 'password': 'mkim', 'port': '22'}")
    f.Run()
    #df.Run()







