#!/usr/bin/env python
"""
 ******************************************************************************
 * Copyright (c) 2016  Juniper Networks. All Rights Reserved.
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

from StringIO import StringIO

from multiprocessing import Pool
from datetime import date, datetime, timedelta

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.exception import *
from lxml import etree
from lxml import objectify
from directFetcher import DirectFetcher

from jnpr.space import rest, async
from jnpr.space.rest import RestException

import zipfile,io    # zip manipulation

TIMEOUT_REST_API = 3

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import xml.etree.ElementTree as ET

import logging
import logging.config

class SNSIFetcher(DirectFetcher):
     
    # Override the load and validate to work from Junos Space instead of intput file
    # return (False,ErrorMessage) if inputs are invalid or (True,SuccessMessage) if they are valid
    def LoadInputFile(self):
        
        devices= []
        general_settings= []

        #### Read the general settings information
        try:
            with open('conf/fullFetcher.conf') as data_file:    
                general_settings = json.load(data_file)
        except:
            msg="Loading and Verifying Device List failed : Unable to read input or parse file 'assistedFetcher.conf' responsible for storing general settings."
            logger.error(msg)
            return (False,msg)
        
        self.THREADCOUNT=int(general_settings["parallelProcesses"])
        
        # Create a Space REST end point

        ### Prepare call to the Junos Space REST API
        url="https://%s/api/juniper/servicenow/devicesnapshot-management/devicesnapshots"%(general_settings["url"])
        auth=HTTPBasicAuth(general_settings["username_js"] , general_settings["password_js"])
        headers = {'accept':'application/vnd.juniper.servicenow.devicesnapshot-management.devicesnapshots+json;version=1'}
        payload=""
        
        #try:
        response = requests.get(url,verify=False,data=payload,headers=headers,auth=auth,timeout=TIMEOUT_REST_API)
        """except:
            msg="Loading and Verifying Device List : Unable to retrive the device list from Junos Space.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""
        """

        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg="Loading and Verifying Device List : The device list from Junos Space is empty.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""
          
        #print(response.text)
        
        result=json.loads(response.text)
        #print(json.dumps(result, indent=4, sort_keys=True))
 
        tmp={}
        #### Build the in-memory structure
        for devicesnapshot in result["devicesnapshots"]["devicesnapshot"]:
            
            hostname=devicesnapshot["hostName"]
            device_snapshot_id=devicesnapshot["@key"]

            entry={}
            entry["username"]=general_settings["username_js"]
            entry["password"]=general_settings["password_js"]
            entry["url"]=general_settings["url"]
            entry["hostname"]=hostname
            entry["href"]=devicesnapshot["@href"]
            entry["device_snapshot_id"]=device_snapshot_id
        
            if hostname in tmp.keys():
                if int(device_snapshot_id) < int(tmp[hostname]["device_snapshot_id"]):
                   tmp[hostname]=entry
            else:
                tmp[hostname]=entry

        self.jobList=tmp.values()      
        msg="Loading and Verifying Device List was successful, loaded (%s) hosts!"%str(len(self.jobList))
        logging.info(msg)
        return (True,msg)

    def cleanNamespace(self,text):
        textEdit = re.sub('<configuration.*>', '', text)
        textEdit = re.sub('</configuration>', '', textEdit)

        it = ET.iterparse(StringIO(textEdit))
        for _, el in it:
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        root = it.root

        string=""



        self.parse_tree(root)
        for value in self.parsedValues:
            string = string + value + "\n"
        self.parsedValues = []
        return string

     # process job OVERIDDED from the directFecther since it uses SpaceEz and not direct connections

    def parse_tree(self, root, commandLine=["set"]):
        #print ("Hello {}".format(root.tag))
        blacklist = {"name","contents","daemon-process"}
        ignore = {"configuration", "undocumented","rpc-reply", "cli"}
        if(root.tag not in ignore):  #!!!ignores comments, and the <configuration> and <rpc-reply> tags and root.tag.find("{")==-1)
            if root.tag not in blacklist:
                commandLine.append(root.tag)
                #print ("{}".format(root.tag))
            if(len(root)==0):
                if(root.text!=None):
                    if len(root.text.strip().replace(" ",""))==len(root.text.strip()):
                        line = " ".join(commandLine) + " " + root.text.strip() + "\n"
                    else:
                        line = " ".join(commandLine) + ' "' + root.text.strip() + '"'
                else:
                    line = " ".join(commandLine) 
                self.parsedValues.append(line.strip())
                #commandLine.pop()
            else:


                if (root[0].tag=="name" and len(root)>1):
                    commandLine.append(root[0].text.strip())
                    for i in xrange(1,len(root)):
                        self.parse_tree(root[i],commandLine)
                    #print ("1 {}".format(commandLine))
                    commandLine.pop()
                else:
                    for child in root:
                        self.parse_tree(child,commandLine)

            #print ("2 {}".format(commandLine))
            if root.tag not in blacklist:
                commandLine.pop()
        elif root.tag == "cli":
            pass
        else:
            for child in root:
                self.parse_tree(child,commandLine)


     # process job OVERIDDED from the directFecther since it uses SpaceEz and not direct connections
    def job(self,args):
        output = {}
        output["router_%s"%args["hostname"]] = "" 
        commandOutput = ""

                
        logging.info("Connecting to: "+args["hostname"])
        
        ###########################################################
        ### Prepare call to the Junos Space REST API
        ###########################################################
        
        url="https://%s%s/"%(args["url"],args["href"],)
        auth=HTTPBasicAuth(args["username"] , args["password"])
        headers = {'accept':'application/vnd.juniper.servicenow.devicesnapshot-management.devicesnapshot+json;version=2'}
        payload=""
        
        #try:
        response = requests.get(url,verify=False,data=payload,headers=headers,auth=auth,timeout=TIMEOUT_REST_API)
        """except:
            msg="Loading and Verifying Device List : Unable to retrive the device list from Junos Space.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""
        """
        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg="Loading and Verifying Device List : The device list from Junos Space is empty.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""
          
        result=json.loads(response.text)
        #print(json.dumps(result, indent=4, sort_keys=True))

        ###########################################################
        ### Download the file attachments
        ###########################################################

        url="https://%s%s/downloadAllAttachments"%(args["url"],args["href"],)
        auth=HTTPBasicAuth(args["username"] , args["password"])
        headers = {'accept':'application/octet-stream'}
        payload=""
        
        #try:
        response = requests.get(url,verify=False,data=payload,headers=headers,auth=auth,timeout=TIMEOUT_REST_API,stream=True)
 
        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg="Loading and Verifying Device List : The device list from Junos Space is empty.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""

 
        #print("File lenght: " + str(len(response.text)))
        
        #Enable to dump gzip files to disk
        #fo=file("dump_"+args["hostname"]+".gz","wb")  
        #fo.write(response.content)                             
        #fo.close()


        try:
            in_memory_zip=io.BytesIO(response.content)    # take the in memory zip file and make it behave like a file handle
            zfile=zipfile.ZipFile(in_memory_zip)          # open the zip file  
        except:
            msg="[%s] Zip file retrieved from Junos Space is invalid."%(args["hostname"])
            logging.error(msg)
            return ""  

        for name in zfile.namelist(): 
            #print("Heloo {0}".format(commandLines[i]))   
            #print("Heloo1 {0}".format(name)) 
            #print("Heloo2 {0}".format(name.find(commandLines[i].strip())))             # list files and detect search for the show display file                  
            if name.find("_shd_xml") >-1:             # found the files
                
                autoDetect=zfile.read(name)+"\n"+"\n"                  # retrive the content
                if autoDetect=="":
                    msg="[%s] Zip file retrieved from Junos Space does not contain the \"%s\" information."%(args["hostname"],commandLines["commandList"][i].strip())
                    logging.error(msg)
                    return commandOutput #will return empty if no file containing "show display" was found containing the show display

                if(autoDetect.find("<description>MX")>-1 or autoDetect.find("<description>VMX")>-1 or autoDetect.find("<description>M")>-1 or autoDetect.find("<description>T")>-1 or autoDetect.find("<description>PTX")>-1 or autoDetect.find("<description>ACX")>-1):
                    try:
                        with open("commands/MX_3.txt", "r") as data_file:
                            commandLines = json.load(data_file)
                            logging.info("Loaded list of commands " + "["+args["host"]+"]")

                    except:
                        msg="Loading and Verifying Device List : Unable to read input file 'commands/MX_3.txt'."
                        logging.error(msg)
                        return (False,msg)

                elif(autoDetect.find("<description>SRX")>-1 or autoDetect.find("<description>VSRX")>-1):
                    try:
                        with open("commands/SRX_3.txt", "r") as data_file:
                            commandLines = json.load(data_file)
                            logging.info("Loaded list of commands " + "["+args["host"]+"]")

                    except:
                        msg="Loading and Verifying Device List : Unable to read input file 'commands/SRX_3.txt'."
                        logging.error(msg)
                        return (False,msg)

                elif(autoDetect.find("<description>QFX")>-1 or autoDetect.find("<description>EX")>-1):
                    try:
                        with open("commands/QFX_3.txt", "r") as data_file:
                            commandLines = json.load(data_file)
                            logging.info("Loaded list of commands " + "["+args["host"]+"]")

                    except:
                        msg="Loading and Verifying Device List : Unable to read input file 'commands/QFX_3.txt'."
                        logging.error(msg)
                        return (False,msg)
                else:
                    msg = "The device was not recognized!"
                    logging.error(msg)   
                    return (False, msg)




        
        try:

            in_memory_zip=io.BytesIO(response.content)    # take the in memory zip file and make it behave like a file handle
            zfile=zipfile.ZipFile(in_memory_zip)          # open the zip file 
        except:
            msg="[%s] Zip file retrieved from Junos Space is invalid."%(args["hostname"])
            logging.error(msg)
            return "" 

        for i in xrange(len(commandLines["commandList"])):    
            for name in zfile.namelist(): 
                #print("Heloo {0}".format(commandLines[i]))   
                #print("Heloo1 {0}".format(name)) 
                #print("Heloo2 {0}".format(name.find(commandLines[i].strip())))             # list files and detect search for the show display file                  
                if name.find(commandLines["commandList"][i].strip()) >-1:             # found the files
                    
                    commandOutput=zfile.read(name)+"\n"+"\n"                  # retrive the contents
                    if commandOutput=="":
                        msg="[%s] Zip file retrieved from Junos Space does not contain the \"%s\" information."%(args["hostname"],commandLines["commandList"][i].strip())
                        logging.error(msg)
                        return commandOutput #will return empty if no file containing "show display" was found containing the show display


                    header="root@"+args["hostname"]+">"
                    if commandLines["commandList"][i].strip()=="_cfg_xml":
                        commandOutput = self.cleanNamespace("""<rpc-reply>"""+commandOutput+"""</rpc-reply>""")

                    commandOutput=header+"\n" + commandOutput + "\n"  # prepare output 


                    output["router_%s"%args["hostname"]]+= commandOutput
                    output[commandLines["commandList"][i].strip()] = commandOutput   
        

        # xcontent = ET.fromstring(output)
        
        #doc = [xcontent.find("title").text, xcontent.find("content").text, xcontent.find("keywords").text]
        #print ("Hello{0}".format(doc[0]))
        #out = open("output.txt", "w")
        #out.write("\n\n".join(doc))



        logging.info ("Done ["+args["hostname"]+"].") 


        

        return output

if __name__ == '__main__':
    logging.config.fileConfig('conf/logging.conf')
    f=SNSIFetcher()
    f.LoadInputFile()
    #f.job("{'username': 'mkim', 'host': '172.30.77.181', 'password': 'mkim', 'port': '22'}")
    #f.job(f.jobList[0])
    f.Run()
    #df.Run()







