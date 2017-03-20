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

import paramiko

from multiprocessing import Pool
from datetime import date, datetime, timedelta

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.exception import *
from lxml import etree

import logging
import logging.config


class DirectFetcher:
 
    def __init__(self, path):
        self.THREADCOUNT=15
        self.jobList=[]
        self.parsedValues=[]
        self.path=path
    
    def __call__(self,args):
        return self.job(args)
    # process job 
    def job(self,args):
        output = {}
        output["router_%s"%args["host"]] = "" 
        commandOutput = ""
        commandCheck = ""
        autoDetect = ""
       
        #args=eval(args)
        logging.info("Connecting to: "+args["host"])
        
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(args["host"], port =22, username=args["username"], password=args["password"])
            #ssh.exec_command('cli')
            ssh_stdin, out, ssh_stderr = ssh.exec_command('cli show chassis hardware detail "|" display xml')
            autoDetect = out.read()
            #print ("Hello {}".format(autoDetect))
        
        except Exception as err:
            logging.error("Error parsing command output ["+args["host"]+"]:", err)
            return ""

        if self.path == "IB":
            output["router_%s"%args["host"]] = autoDetect
            output['show chassis hardware detail | display xml']=autoDetect
            return output
        #print ("{}".format(self.path))

        if(autoDetect.find("<description>MX")>-1 or autoDetect.find("<description>M")>-1 or autoDetect.find("<description>T")>-1 or autoDetect.find("<description>PTX")>-1 or autoDetect.find("<description>ACX")>-1):
            try:
                with open("commands/MX_12.txt", "r") as data_file:
                    commandSettings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["host"]+"]")

            except:
                msg="Loading and Verifying Device List : Unable to read input file 'commands/MX_12.txt'."
                logging.error(msg)
                return (False,msg)

        elif(autoDetect.find("<description>SRX")>-1):
            try:
                with open("commands/SRX_12.txt", "r") as data_file:
                    commandSettings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["host"]+"]")

            except:
                msg="Loading and Verifying Device List : Unable to read input file 'commands/SRX_12.txt'."
                logging.error(msg)
                return (False,msg)

        elif(autoDetect.find("<description>QFX")>-1 or autoDetect.find("<description>EX")>-1):
            try:
                with open("commands/QFX_12.txt", "r") as data_file:
                    commandSettings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["host"]+"]")

            except:
                msg="Loading and Verifying Device List : Unable to read input file 'commands/QFX_12.txt'."
                logging.error(msg)
                return (False,msg)
        else:
            msg = "The device was not recognized!"
            logging.error(msg)   
            return (False, msg)

        try:
            for i in xrange(len(commandSettings["commandList"])):
                #print ("{}".format(len(commandSettings["commandList"])))
                commandCheck = commandSettings["commandList"][i].strip()
                if (commandCheck.split(" ",1)[0]=="show" or commandCheck =="request support information"):
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("cli "+re.sub('[|]', '"|"', commandCheck))
                    commandOutput = "root@%s> %s\n"%(args["host"],commandCheck)
                    commandOutput = commandOutput + (ssh_stdout.read()) + "\n\n\n"
                    #print ("{}".format(commandOutput))
                    output["router_%s"%args["host"]] += commandOutput
                    output[commandCheck] = commandOutput
            ssh.exec_command('exit')
        except Exception as err:
            logging.error("Error parsing command output ["+args["host"]+"]:", err)
            return ""
        
        return output
      
    # load and validate intput file return (False,ErrorMessage) if inputs are invalid or (True,SuccessMessage) if they are valid
    def LoadInputFile(self):
        
        hosts_lines= []
        general_settings= []

        
        #### read the device list from input file
        try:
            with open("hosts.csv", "r") as hosts_file:
                hosts_lines = hosts_file.readlines()
        except:
            msg="Loading and Verifying Device List : Unable to read input file 'hosts.csv'."
            logging.error(msg)
            return (False,msg)
        #### read the general settings information
        try:
            with open('conf/directFetcher.conf') as data_file:    
                general_settings = json.load(data_file)
        except:
            msg="Loading and Verifying Device List : Unable to read input or parse file 'directFetcher.conf' responsible for storing general settings."
            logging.error(msg)
            return (False,msg)
        self.THREADCOUNT=int(general_settings["parallelProcesses"])
        
        #### build the in-memory structure
        for host_line in hosts_lines:
            host_line = host_line.strip(' \t\n\r')
            ## Skip empty lines
            if host_line == "" :
                continue;
            ## Skip if line begins with '#''
            if host_line[0] == ord('#'):
                continue;
            host_entry={}
            items=host_line.split(",")
            if len(items) == 1:
                if not type(general_settings["port"]) is  list:
                    general_settings["port"]=[general_settings["port"]]
                for port in general_settings["port"]:
                    host_entry["host"]=items[0]
                    host_entry["username"]=general_settings["username"]
                    host_entry["password"]=general_settings["password"]
                    host_entry["port"]=port
                    self.jobList.append((host_entry))
            if len(items) == 4:
                host_entry["host"]=items[0]
                host_entry["username"]=items[1]
                host_entry["password"]=items[2]
                host_entry["port"]=items[3]
                self.jobList.append((host_entry))
            
        #print(self.jobList)
        msg="Loading and Verifying Device List : Successful, loaded (%s) hosts!"%str(len(self.jobList))
        logging.info(msg)
        return (True,msg)
    def Run(self):
        p = Pool(self.THREADCOUNT)
        ret=p.map(self,self.jobList)
        #print ("HEllo {0}".format((self.jobList).size()))
        #ret = []
        #ret.append(self.job(self.jobList[0]))
        #ret.append(self.job(self.jobList[1]))
        #print ("Result %s"% (self.jobList[0]['host']))
        #print ("Result %s"% ret[0])
        success = 0
        failed = 0


        
        try:

            for key, value in ret[0].items():
                mod = re.sub('\|','',key)
                #print("{}".format(mod))
                outputName = re.sub(' ','_',mod)

                
                fo = open("output/%s.xml"%outputName, "w")
                fo.write(value)
                for i in range(1,len(ret)):
                    for keyOther, valueOther in ret[i].items():
                        if key == keyOther:
                            fo.write(valueOther)
                        if keyOther.split("_",1)[0] == "router":
                            host = open("output/%s.xml"%keyOther, "w")
                            host.write(valueOther)
                            host.close()
                #hosts = fo.write(value)
            
                fo.close()
        except:
            msg="No output was received from the devices."
            logging.error(msg)
            return (False,msg)
        #msg="Retriving the information from devices : Process finished [failed hosts (%s) | success hosts (%s)] "%(failed,success)
        msg="Retriving the information from devices : Process finished"
        logging.info(msg)
        return (True,msg) 
if __name__ == '__main__':

    logging.config.fileConfig('conf/logging.conf')
    df=DirectFetcher(sys.argv[1])
    df.LoadInputFile()
    # To test single process job  for debugging purposes use the following: 
    #df.job("{'username': 'mkim', 'host': '172.30.77.181', 'password': 'mkim', 'port': '22'}")
    df.Run()
    #df.Run()
