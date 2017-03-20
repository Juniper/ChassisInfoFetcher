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

TIMEOUT_REST_API = 3

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import logging
import logging.config

class FullFetcher(DirectFetcher):
     
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
        space = rest.Space(url="https://"+general_settings["url"], user=general_settings["username_js"], passwd=general_settings["password_js"])
        logging.info("Connecting to Junos Space to retrieve the devices list.")
        try:
            devices = space.device_management.devices.\
                  get(filter_={'deviceFamily': 'junos',
                                'connectionStatus': 'up'})
        except RestException as ex:
            msg="An errror occured during the communication with the Junos Space API.\n\tHTTP error code : %s;\n\tJunos Space Message : %s "%(ex.response,ex.response.text)
            logging.error(msg)
            return ("False",msg)

        #### Build the in-memory structure
        for device in devices:
            entry={}
            entry["username"]=general_settings["username_js"]
            entry["password"]=general_settings["password_js"]
            entry["url"]=general_settings["url"]
            entry["serialNumber"]=str(device.serialNumber)
            entry["ipAddr"]=str(device.ipAddr)
            entry["name"]=str(device.name)

            self.jobList.append(entry)
        
        #print(self.jobList)
        msg="Loading and Verifying Device List was successful, loaded (%s) hosts!"%str(len(self.jobList))
        logging.info(msg)
        return (True,msg)

    def unwrap(self, text):

        tagToUnwrap = ["replyMsgData", "configuration-information", "configuration-output"]
        for i in xrange(len(tagToUnwrap)):
            text = re.sub('<'+tagToUnwrap[i]+'.*>', '', text)
            text = re.sub('</'+tagToUnwrap[i]+'>', '', text)
        return text

    def cleanNamespace(self,text):
        it = etree.iterparse(StringIO(text))
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

    def parse_tree(self, root, commandLine=[""]):
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

    def job(self,args):
        output = {}
        output["router_%s"%args["ipAddr"]] = ""
        commandOutput = ""
        commandCheck = ""
        flag = 0

        
        logging.info("Connecting to: "+args["ipAddr"])

      
        try:
            space = rest.Space("https://"+args["url"], args["username"], args["password"])

            autoDetect=space.device_management.devices.\
                          get(filter_={'serialNumber': args["serialNumber"] })[0].\
                          exec_rpc.post(rpcCommand="<command>show chassis hardware</command>")

        except RestException as ex:
            logging.error("An errror occured during the communication with the Junos Space API.\n\tHTTP error code : %s;\n\tJunos Space Message : %s "%(ex.response,ex.response.text))
            return ""

        autoDetect = etree.tostring(autoDetect, pretty_print=True)

        if self.path == "IB":
            output["router_%s"%args["ipAddr"]] = autoDetect
            output['show chassis hardware detail | display xml']=autoDetect
            return output
            
        if(autoDetect.find("<description>MX")>-1 or autoDetect.find("<description>M")>-1 or autoDetect.find("<description>T")>-1 or autoDetect.find("<description>PTX")>-1 or autoDetect.find("<description>ACX")>-1):
            try:
                with open("commands/MX_4.txt", "r") as data_file:
                    commandSettings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["ipAddr"]+"]")

            except:
                msg="Loading and Verifying Device List : Unable to read input file 'commands/MX_4.txt.'."
                logging.error(msg)
                return (False,msg)

        elif(autoDetect.find("<description>SRX")>-1):
            try:
                with open("commands/SRX_4.txt", "r") as data_file:
                    commandSettings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["ipAddr"]+"]")

            except:
                msg="Loading and Verifying Device List : Unable to read input file 'commands/SRX_4.txt'."
                logging.error(msg)
                return (False,msg)

        elif(autoDetect.find("<description>QFX")>-1 or autoDetect.find("<description>EX")>-1):
            try:
                with open("commands/QFX_4.txt", "r") as data_file:
                    commandSettings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["ipAddr"]+"]")

            except:
                msg="Loading and Verifying Device List : Unable to read input file 'commands/QFX_4.txt'."
                logging.error(msg)
                return (False,msg)
        else:
            msg = "The device was not recognized!"
            logging.error(msg)   
            return (False, msg)



        for i in xrange(len(commandSettings["commandList"])):
            #print ("Command {0}".format(commandSettings["commandList"][i].strip()))
            commandCheck = commandSettings["commandList"][i].strip()  #commandCheck contains the current command being evaluated 

            if ((commandCheck.split(" ",1)[0]=="show" or commandCheck =="request support information") and commandCheck.split("|")[-1].strip() != "display xml"):

                result=space.device_management.devices.\
                      get(filter_={'serialNumber': args["serialNumber"] })[0].\
                      exec_rpc.post(rpcCommand="<command>" + commandCheck + "</command>")

                output_xml=result.xpath('netConfReplies/netConfReply/replyMsgData')

                if len(output_xml)!=1:
                    logging.error("The reply from the server does not contain a valid \""+commandCheck+"\" reply. Full reply was logged in DEBUG level.")
                    logging.debug(etree.tostring(output_xml, pretty_print=True))
                    return ""

                output_text=etree.tostring(output_xml[0], pretty_print=True)
                finalText = self.unwrap(output_text)
                #if (commandCheck.find("configuration")==-1):
                #    finalText = self.cleanNamespace(finalText)

                


                commandOutput = "root@%s> %s\n"%(args["ipAddr"],commandCheck) + finalText + "\n\n\n"
                output["router_%s"%args["ipAddr"]] += commandOutput         #Preparation for the two types of output: file_host1 contains the output of all the commands ran on host1;
                output[commandCheck] = commandOutput                    #file_show_chassis_hardware contains the output of the "show chassis harware" command from all hosts
            else:
                logging.error("The following command is not allowed : %s "%(commandCheck))   
                return output                 
                
 

        #output ="root@%s> show chassis hardware detail | display xml | no-more\n"%(args["name"])
        #output += 

            
        logging.info ("Done ["+args["ipAddr"]+"].") 
        return output

if __name__ == '__main__':
    logging.config.fileConfig('conf/logging.conf')
    f=FullFetcher(sys.argv[1])
    f.LoadInputFile()
    #f.job("{'username': 'mkim', 'host': '172.30.77.181', 'password': 'mkim', 'port': '22'}")
    #f.job(f.jobList[0])
    f.Run()
    #df.Run()







