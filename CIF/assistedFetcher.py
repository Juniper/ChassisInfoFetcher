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
import sys
import json
import logging
import logging.config

from directFetcher import DirectFetcher

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

TIMEOUT_REST_API = 3

class AssistedFetcher(DirectFetcher):

    # Override the load and validate to work from Junos Space instead of intput file
    # return (False,ErrorMessage) if inputs are invalid or (True,SuccessMessage) if they are valid
    def LoadInputFile(self):

        general_settings = []

        #### Read the general settings information
        try:
            with open('conf/assistedFetcher.conf') as data_file:
                general_settings = json.load(data_file)
        except IOError:
            msg = "Loading and Verifying Device List : Unable to read input or parse file 'assistedFetcher.conf' responsible for storing general settings."
            logging.error(msg)
            return (False, msg)

        self.THREADCOUNT = int(general_settings["parallelProcesses"])

        ### Prepare call to the Junos Space REST API
        url = "https://%s/api/space/device-management/devices" % (general_settings["url"])
        auth = HTTPBasicAuth(general_settings["js_username"], general_settings["js_password"])
        headers = {'accept':'application/vnd.net.juniper.space.device-management.devices+json;version=1'}
        payload = ""

        try:
            response = requests.get(url, verify=False, data=payload, headers=headers, auth=auth, timeout=TIMEOUT_REST_API)
        except requests.exceptions.RequestException:
            msg = "Loading and Verifying Device List : Unable to retrive the device list from Junos Space."
            logging.error(msg)
            return (False, msg)

        ### Treat an empty reply as a error
        if response.status_code == 204:
            msg = "Loading and Verifying Device List : The device list from Junos Space is empty."
            logging.error(msg)
            return (False, msg)

        try:
            result = json.loads(response.text)
        #Note
        except IOError:
            msg = "Unable to interpret the json file response.\n       Junos Space response is the following :\n       " + response.text
            logging.error(msg)
            return (False, msg)


        #### Build the in-memory structure
        for device in result["devices"]["device"]:
            host_entry = {}

            for port in general_settings["port"]:
                host_entry["host"] = device["ipAddr"]
                host_entry["username"] = general_settings["device_ssh_username"]
                host_entry["password"] = general_settings["device_ssh_password"]
                host_entry["port"] = port
                self.jobList.append(host_entry)

        #print(self.jobList)
        msg = "Loading and Verifying Device List : Successful, loaded (%s) hosts!" % str(len(self.jobList))
        logging.info(msg)
        return (True, msg)

if __name__ == '__main__':
    logging.config.fileConfig('conf/logging.conf')
    ASSISTED = AssistedFetcher(sys.argv[1])
    logging.info(ASSISTED.LoadInputFile())

    ASSISTED.Run()
