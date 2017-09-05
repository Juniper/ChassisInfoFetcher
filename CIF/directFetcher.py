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
import re
import json
from multiprocessing import Pool

import logging
import logging.config

import paramiko



class DirectFetcher(object):
    '''
    Connect to the specified devices in parallel and fetch the required information.

    Get the ip addresses specified in the hosts.csv file, the login information in the settings menu of the app and connect to the devices in parallel.
    Collect either the Install Base information or information about the Advanced Service deliverables, depending on what is selected in the menu.
    '''

    def __init__(self, path):
        self.THREADCOUNT = 15
        self.jobList = []
        self.parsedValues = []
        self.path = path

    def __call__(self, args):
        return self.job(args)

    def job(self, args):
        '''
        Connect to the specified host, execute a set of commands and provide the output to be written into the corresponding file.

        If path = IB, only the chassis information is fetched from the specified device. Otherwise, if path = AS, then based on the type of device (MX/SRS/QFX) a predefined
        set of commands are executed. Only "show" commands and the "request support information" command can be executed on the devices.
        '''

        output = {}
        output["router_%s" % args["host"]] = ""
        command_output = ""
        command_check = ""
        auto_detect = ""

        logging.info("Connecting to: " + args["host"])

        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(args["host"], port=22, username=args["username"], password=args["password"])

            #How to get just the out variable
            _, out, _ = ssh.exec_command('cli show chassis hardware detail "|" display xml')
            auto_detect = out.read()

        #Note
        except (BadHostKeyException, AuthenticationException, SSHException, socket.error) as err:
            logging.error("Error parsing command output ["+args["host"]+"]:", err)
            return ""

        if self.path == "IB":
            output["router_%s" % args["host"]] = auto_detect
            output['show chassis hardware detail | display xml'] = auto_detect
            return output

        if auto_detect.find("<description>MX") > -1 or auto_detect.find("<description>VMX") > -1 or auto_detect.find("<description>M") > -1 or auto_detect.find("<description>T") > -1 or auto_detect.find("<description>PTX") > -1 or auto_detect.find("<description>ACX") > -1:
            try:
                with open("commands/MX_12.txt", "r") as data_file:
                    command_settings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["host"]+"]")

            except IOError as err:
                msg = "Loading and Verifying Device List : Unable to read input file 'commands/MX_12.txt'."
                logging.error(msg)
                return (False, msg)

        elif auto_detect.find("<description>SRX") > -1 or auto_detect.find("<description>VSRX") > -1:
            try:
                with open("commands/SRX_12.txt", "r") as data_file:
                    command_settings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["host"]+"]")

            except IOError as err:
                msg = "Loading and Verifying Device List : Unable to read input file 'commands/SRX_12.txt'."
                logging.error(msg)
                return (False, msg)

        elif auto_detect.find("<description>QFX") > -1 or auto_detect.find("<description>EX") > -1:
            try:
                with open("commands/QFX_12.txt", "r") as data_file:
                    command_settings = json.load(data_file)
                    logging.info("Loaded list of commands " + "["+args["host"]+"]")

            except IOError as err:
                msg = "Loading and Verifying Device List : Unable to read input file 'commands/QFX_12.txt'."
                logging.error(msg)
                return (False, msg)
        else:
            msg = "The device was not recognized!"
            logging.error(msg)
            return (False, msg)

        try:
            for i in range(len(command_settings["commandList"])):

                command_check = command_settings["commandList"][i].strip()
                if command_check.split(" ", 1)[0] == "show" or command_check == "request support information":
                    _, ssh_stdout, _ = ssh.exec_command("cli " + re.sub('[|]', '"|"', command_check))
                    command_output = "root@%s> %s\n" % (args["host"], command_check)
                    command_output = command_output + (ssh_stdout.read()) + "\n\n\n"

                    output["router_%s" % args["host"]] += command_output
                    output[command_check] = command_output
            ssh.exec_command('exit')
        except IOError as err:
            logging.error("Error parsing command output [" + args["host"]+"]:", err)
            return ""

        logging.info("Done [" + args["host"]+"].")

        return output

    def LoadInputFile(self):
        '''
        Read the hosts.csv file in order to get the list of devices to which the tool should connect.

        If the list of devices in the host file also contains the username, password and port number, use those instead of the ones specified in the settings menu in the GUI.
        '''
        hosts_lines = []
        general_settings = []

        # Read the device list from input file
        try:
            with open("hosts.csv", "r") as hosts_file:
                hosts_lines = hosts_file.readlines()
        except IOError:
            msg = "Loading and Verifying Device List : Unable to read input file 'hosts.csv'."
            logging.error(msg)
            return (False, msg)
        # Read the general settings information
        try:
            with open('conf/directFetcher.conf') as data_file:
                general_settings = json.load(data_file)
        except IOError:
            msg = "Loading and Verifying Device List : Unable to read input or parse file 'directFetcher.conf' responsible for storing general settings."
            logging.error(msg)
            return (False, msg)
        self.THREADCOUNT = int(general_settings["parallelProcesses"])

        # Build the in-memory structure
        for host_line in hosts_lines:
            host_line = host_line.strip(' \t\n\r')
            # Skip empty lines
            if host_line == "":
                continue
            # Skip if line begins with '#''
            if host_line[0] == ord('#'):
                continue
            host_entry = {}
            items = host_line.split(",")
            # In this case the items list contains only the ip address of the device, so get the rest of the information from the settings menu in the GUI.
            if len(items) == 1:
                if not isinstance(general_settings["port"], list):
                    general_settings["port"] = [general_settings["port"]]
                for port in general_settings["port"]:
                    host_entry["host"] = items[0]
                    host_entry["username"] = general_settings["username"]
                    host_entry["password"] = general_settings["password"]
                    host_entry["port"] = port
                    self.jobList.append((host_entry))
            # In this case the items list contains all the information including the ip address of the device and the login information
            if len(items) == 4:
                host_entry["host"] = items[0]
                host_entry["username"] = items[1]
                host_entry["password"] = items[2]
                host_entry["port"] = items[3]
                self.jobList.append((host_entry))

        msg = "Loading and Verifying Device List : Successful, loaded (%s) hosts!" % str(len(self.jobList))
        logging.info(msg)
        return (True, msg)

    def Run(self):
        '''
        Run the job function for each device, get the output and sort it into files based on device ip and type of command.

        The output from each device is written in separate file. Additionally, the output from all devices for a specific command (i.e. show configuration | display set) is
        written into one file.
        '''
        job_pool = Pool(self.THREADCOUNT)
        ret = job_pool.map(self, self.jobList)


        try:

            for key, value in ret[0].items():
                mod = re.sub('\|', '', key)
                output_name = re.sub(' ', '_', mod)

                file_write = open("output/%s.xml" % output_name, "w")
                file_write.write(value)
                for i in range(1, len(ret)):
                    for key_other, value_other in ret[i].items():
                        if key == key_other:
                            file_write.write(value_other)
                        if key_other.split("_", 1)[0] == "router":
                            host = open("output/%s.xml" % key_other, "w")
                            host.write(value_other)
                            host.close()

                file_write.close()
        except IOError:
            msg = "No output was received from the devices."
            logging.error(msg)
            return (False, msg)
        msg = "Retriving the information from devices : Process finished"
        logging.info(msg)
        return (True, msg)
if __name__ == '__main__':

    logging.config.fileConfig('conf/logging.conf')
    # The arguement that needs to be provided is either IB or AS, based on the type of the informatin that needs to be collected. AS - Advanced Service deliverables;
    # IB = Install Base
    DIRECT = DirectFetcher(sys.argv[1])
    DIRECT.LoadInputFile()

    DIRECT.Run()
