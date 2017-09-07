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

import re
import json
import sys
import zipfile
import io
import xml.etree.ElementTree as ET

import logging
import logging.config


from StringIO import StringIO

from directFetcher import DirectFetcher



TIMEOUT_REST_API = 3

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class SNSIFetcher(DirectFetcher):

    # Override the load and validate to work from Junos Space instead of intput file
    # return (False,ErrorMessage) if inputs are invalid or (True,SuccessMessage) if they are valid
    def LoadInputFile(self):

        devices = []
        general_settings = []

        #### Read the general settings information
        try:
            with open('conf/SNSIFetcher.conf') as data_file:
                general_settings = json.load(data_file)
        except IOError:
            msg = "Loading and Verifying Device List failed : Unable to read input or parse file 'assistedFetcher.conf' responsible for storing general settings."
            logging.error(msg)
            return (False, msg)

        self.THREADCOUNT = int(general_settings["parallelProcesses"])

        # Create a Space REST end point

        ### Prepare call to the Junos Space REST API
        url = "https://%s/api/juniper/servicenow/devicesnapshot-management/devicesnapshots"%(general_settings["url"])
        auth = HTTPBasicAuth(general_settings["username_js"] , general_settings["password_js"])
        headers = {'accept':'application/vnd.juniper.servicenow.devicesnapshot-management.devicesnapshots+json;version=1'}
        payload = ""

        #try:
        response = requests.get(url, verify=False, data=payload, headers=headers, auth=auth,timeout=TIMEOUT_REST_API)
        """except:
            msg="Loading and Verifying Device List : Unable to retrive the device list from Junos Space.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""
        """

        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg = "Loading and Verifying Device List : The device list from Junos Space is empty.\n   Junos Space Message : \n   " + response.text
            logging.error(msg)
            return ""

        result = json.loads(response.text)

        tmp = {}
        #### Build the in-memory structure
        for devicesnapshot in result["devicesnapshots"]["devicesnapshot"]:

            hostname = devicesnapshot["hostName"]
            device_snapshot_id = devicesnapshot["@key"]

            entry = {}
            entry["username"] = general_settings["username_js"]
            entry["password"] = general_settings["password_js"]
            entry["url"] = general_settings["url"]
            entry["hostname"] = hostname
            entry["href"] = devicesnapshot["@href"]
            entry["device_snapshot_id"] = device_snapshot_id

            if hostname in tmp.keys():
                if int(device_snapshot_id) < int(tmp[hostname]["device_snapshot_id"]):
                   tmp[hostname] = entry
            else:
                tmp[hostname] = entry

        self.jobList = tmp.values()
        msg = "Loading and Verifying Device List was successful, loaded (%s) hosts!" % str(len(self.jobList))
        logging.info(msg)
        return (True, msg)

    def cleanNamespace(self, text):
        textEdit = re.sub('<configuration.*>', '', text)
        textEdit = re.sub('</configuration>', '', textEdit)

        it = ET.iterparse(StringIO(textEdit))
        for _, el in it:
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        root = it.root

        string = ""



        self.parse_tree(root)
        for value in self.parsedValues:
            string = string + value + "\n"
        self.parsedValues = []
        return string

     # process job OVERIDDED from the directFecther since it uses SpaceEz and not direct connections

    def parse_tree(self, root, commandLine=["set"]):
        blacklist = {"name", "contents", "daemon-process"}
        ignore = {"configuration", "undocumented","rpc-reply", "cli"}
        if root.tag not in ignore:  #!!!ignores comments, and the <configuration> and <rpc-reply> tags and root.tag.find("{")==-1)
            if root.tag not in blacklist:
                commandLine.append(root.tag)
            if len(root) == 0:
                if root.text != None:
                    if len(root.text.strip().replace(" ","")) == len(root.text.strip()):
                        line = " ".join(commandLine) + " " + root.text.strip() + "\n"
                    else:
                        line = " ".join(commandLine) + ' "' + root.text.strip() + '"'
                else:
                    line = " ".join(commandLine)
                self.parsedValues.append(line.strip())
            else:


                if root[0].tag == "name" and len(root) > 1:
                    commandLine.append(root[0].text.strip())
                    for i in xrange(1, len(root)):
                        self.parse_tree(root[i], commandLine)

                    commandLine.pop()
                else:
                    for child in root:
                        self.parse_tree(child, commandLine)

            if root.tag not in blacklist:
                commandLine.pop()
        elif root.tag == "cli":
            pass
        else:
            for child in root:
                self.parse_tree(child, commandLine)


     # process job OVERIDDED from the directFecther since it uses SpaceEz and not direct connections
    def job(self, args):
        output = {}
        output["router_%s" % args["hostname"]] = ""
        commandOutput = ""


        logging.info("Connecting to: " + args["hostname"])

        ###########################################################
        ### Prepare call to the Junos Space REST API
        ###########################################################

        url = "https://%s%s/" % (args["url"], args["href"],)
        auth = HTTPBasicAuth(args["username"] , args["password"])
        headers = {'accept':'application/vnd.juniper.servicenow.devicesnapshot-management.devicesnapshot+json;version=2'}
        payload = ""

        #try:
        response = requests.get(url, verify=False, data=payload, headers=headers, auth=auth, timeout=TIMEOUT_REST_API)
        """except:
            msg="Loading and Verifying Device List : Unable to retrive the device list from Junos Space.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""
        """
        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg = "Loading and Verifying Device List : The device list from Junos Space is empty.\n   Junos Space Message : \n   " + response.text
            logging.error(msg)
            return ""

        result = json.loads(response.text)

        ###########################################################
        ### Download the file attachments
        ###########################################################

        url = "https://%s%s/downloadAllAttachments" % (args["url"], args["href"],)
        auth = HTTPBasicAuth(args["username"], args["password"])
        headers = {'accept':'application/octet-stream'}
        payload = ""

        #try:
        response = requests.get(url, verify=False, data=payload, headers=headers, auth=auth, timeout=TIMEOUT_REST_API, stream=True)

        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg = "Loading and Verifying Device List : The device list from Junos Space is empty.\n   Junos Space Message : \n   "+response.text
            logging.error(msg)
            return ""


        try:
            in_memory_zip = io.BytesIO(response.content)    # take the in memory zip file and make it behave like a file handle
            zfile = zipfile.ZipFile(in_memory_zip)          # open the zip file
        except:
            msg = "[%s] Zip file retrieved from Junos Space is invalid." % (args["hostname"])
            logging.error(msg)
            return ""

        for name in zfile.namelist():

            if name.find("_shd_xml") > -1:             # found the files

                if self.path == "IB":
                    output["router_%s"%args["hostname"]] = zfile.read(name)
                    output['show chassis hardware detail | display xml'] = zfile.read(name)
                    return output

                autoDetect = zfile.read(name) + "\n" + "\n"                  # retrive the content
                if autoDetect == "":
                    msg = "[%s] Zip file retrieved from Junos Space does not contain the necessary information." % (args["hostname"])
                    logging.error(msg)
                    return commandOutput #will return empty if no file containing "show display" was found containing the show display

                if autoDetect.find("<description>MX") > -1 or autoDetect.find("<description>VMX") > -1 or autoDetect.find("<description>M") > -1 or autoDetect.find("<description>T") > -1 or autoDetect.find("<description>PTX") > -1 or autoDetect.find("<description>ACX") > -1:
                    try:
                        with open("commands/MX_3.txt", "r") as data_file:
                            commandLines = json.load(data_file)
                            logging.info("Loaded list of commands " + "["+args["hostname"]+"]")

                    except IOError:
                        msg = "Loading and Verifying Device List : Unable to read input file 'commands/MX_3.txt'."
                        logging.error(msg)
                        return (False, msg)

                elif autoDetect.find("<description>SRX") > -1 or autoDetect.find("<description>VSRX") > -1:
                    try:
                        with open("commands/SRX_3.txt", "r") as data_file:
                            commandLines = json.load(data_file)
                            logging.info("Loaded list of commands " + "["+args["hostname"]+"]")

                    except IOError:
                        msg = "Loading and Verifying Device List : Unable to read input file 'commands/SRX_3.txt'."
                        logging.error(msg)
                        return (False, msg)

                elif autoDetect.find("<description>QFX") > -1 or autoDetect.find("<description>EX") > -1:
                    try:
                        with open("commands/QFX_3.txt", "r") as data_file:
                            commandLines = json.load(data_file)
                            logging.info("Loaded list of commands " + "["+args["hostname"]+"]")

                    except IOError:
                        msg = "Loading and Verifying Device List : Unable to read input file 'commands/QFX_3.txt'."
                        logging.error(msg)
                        return (False, msg)
                else:
                    msg = "The device was not recognized!"
                    logging.error(msg)
                    return (False, msg)


        try:

            in_memory_zip = io.BytesIO(response.content)    # take the in memory zip file and make it behave like a file handle
            zfile = zipfile.ZipFile(in_memory_zip)          # open the zip file
        except IOError:
            msg = "[%s] Zip file retrieved from Junos Space is invalid."%(args["hostname"])
            logging.error(msg)
            return ""

        for i in xrange(len(commandLines["commandList"])):
            for name in zfile.namelist():
                # list files and detect search for the show display file
                if name.find(commandLines["commandList"][i].strip()) > -1:             # find the files

                    commandOutput = zfile.read(name)+"\n"+"\n"                  # retrive the contents
                    if commandOutput == "":
                        msg = "[%s] Zip file retrieved from Junos Space does not contain the \"%s\" information." % (args["hostname"], commandLines["commandList"][i].strip())
                        logging.error(msg)
                        return commandOutput #will return empty if no file containing "show display" was found containing the show display


                    header = "root@" + args["hostname"]+"> "
                    if commandLines["commandList"][i].strip() == "_cfg_xml":
                        commandOutput = self.cleanNamespace("""<rpc-reply>""" + commandOutput + """</rpc-reply>""")

                    commandOutput = header + "\n" + commandOutput + "\n"  # prepare output


                    output["router_%s" % args["hostname"]] += commandOutput
                    output[commandLines["commandList"][i].strip()] = commandOutput


        logging.info("Done ["+args["hostname"]+"].")

        return output

if __name__ == '__main__':
    logging.config.fileConfig('conf/logging.conf')
    SNSI = SNSIFetcher(sys.argv[1])
    SNSI.LoadInputFile()

    SNSI.Run()
