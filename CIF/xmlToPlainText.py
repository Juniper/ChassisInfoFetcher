#!/usr/bin/env python
# <*******************
# 
#   Copyright (c) 2017 Juniper Networks . All rights reserved.
#   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the 
#   documentation and/or other materials provided with the distribution.
#
#   3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this 
#   software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
#   EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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

import paramiko

from StringIO import StringIO

from multiprocessing import Pool
from datetime import date, datetime, timedelta

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.exception import *
from lxml import etree as ET

import logging
import logging.config



class XMLToPlainText:

    def __init__(self):
        self.parsedValues=[]

    def __call__(self,args):
        return self.cleanNamespace("<hello></hello>")


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




if __name__ == '__main__':

    logging.config.fileConfig('conf/logging.conf')
    try:
        with open('conf/xmlToPlainText.conf') as data_file:    
            fileNames = json.load(data_file)
    except:
        msg="Loading and Verifying File List : Unable to read input or parse file 'xmlToPlainText.conf' responsible for storing input and output file names for xml to plaintext transformation."
        logging.error(msg)
        sys.exit(1)

    try:
        with open(fileNames["input"], "r") as data_file:
            text = data_file.read()
    except:
        msg="Loading and Verifying File List : Unable to read input or parse file 'xmlToPlainText.conf' responsible for storing input and output file names for xml to plaintext transformation."
        logging.error(msg)
        sys.exit(1)

    df=XMLToPlainText()
    text = df.cleanNamespace(text)

    # To test single process job  for debugging purposes use the following: 
    #df.job("{'username': 'mkim', 'host': '172.30.77.181', 'password': 'mkim', 'port': '22'}")
    try:
        with open(fileNames["output"], "w") as data_file:
            data_file.write(text)
    except:
        msg="Unable to write output file."
        logging.error(msg)
        sys.exit(1) 