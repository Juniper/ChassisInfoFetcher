# coding: utf-8
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
import json

import urwid
from directFetcher import DirectFetcher
from ui_dialog import ui_dialog
import utils

class ui_directFetcher(ui_dialog):


    # direct mode main dialog
    def ShowDialog(self, button):
        caption = urwid.Text(('standoutLabel', u'Direct Mode'))
        helps = urwid.Text([u'In the direct mode the tool will retrieve the device list from \'hosts.csv\' file, will proceed to connect on all devices in a parallel fashion and retrieve the requested chassis information.'])

        general_settings = self.menu_button(u'Settings', self.directFetcher_general_settings_dialog)

        fetch_install_base = self.menu_button(u'Fetch Install Base information', self.directFetcher_IB)
        fetch_as_deliverable = self.menu_button(u'Fetch information for Advanced Service deliverables', self.directFetcher_AS)
        #run_button = self.menu_button(u'Run', self.directFetcher_run)
        cancel_button = self.menu_button(u'Cancel', self.exit_window)
        self.top.open_box(urwid.Pile([caption, urwid.Divider(), helps, urwid.Divider(), general_settings, fetch_install_base, fetch_as_deliverable, cancel_button]))


    def directFetcher_IB(self, button):
        caption = urwid.Text(('standoutLabel', u'Direct Mode > Install Base'))

        verify_file_button = self.menu_button(u'Verify \'hosts.csv\' ', self.directFetcher_verify)
        run_button = self.menu_button(u'Run', self.directFetcherIB_run)
        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), verify_file_button, run_button, cancel_button]))

    def directFetcher_AS(self, button):
        caption = urwid.Text(('standoutLabel', u'Direct Mode > Advanced Service Deliverables'))

        commandSettings = self.menu_button(u'Commands', self.directFetcher_commandSettings_dialog)
        verify_file_button = self.menu_button(u'Verify \'hosts.csv\' ', self.directFetcher_verify)
        run_button = self.menu_button(u'Run', self.directFetcherAS_run)
        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), commandSettings, verify_file_button, run_button, cancel_button]))

    # direct mode > run  | creates the DirectFetcher object and runs the appropiate console tool
    def directFetcherIB_run(self, button):
        with open("execute.task", 'w') as file_handle:
            file_handle.write("DirectFetcherIB")

        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher

    def directFetcherAS_run(self, button):
        with open("execute.task", 'w') as file_handle:
            file_handle.write("DirectFetcherAS")
        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher


    # direct mode > general settings window
    def directFetcher_general_settings_dialog(self, button):
        caption = urwid.Text(('standoutLabel', u'Direct Mode > Settings'))
        helps = urwid.Text([u'Please fill in the default username / password / port for SSH. If the number of specified processes are more than the devices that the tool collects information from, then the tool can create parallel sessions for all devices and complete execution faster (this uses up more resources on the machine running the tool).'])


        tb_username = urwid.Edit(('textbox', u"Username :\n"))
        tb_password = urwid.Edit(('textbox', u"Password :\n"), mask="*")
        tb_port = urwid.Edit(('textbox', u"Port :\n"))
        tb_parallel_processes = urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        ### loading previouse settings
        def load_settings():
            try:
                settings = None
                with open('conf/directFetcher.conf') as data_file:
                    settings = json.load(data_file)
                tb_username.set_edit_text(settings["username"])
                tb_password.set_edit_text(settings["password"])
                ### loading the ports list from the json array format needs flattening
                str_port = ""
                for port in settings["port"]:
                    str_port += port + ","
                str_port = str_port.strip(",")
                tb_port.set_edit_text(str_port)
                tb_parallel_processes.set_edit_text(settings["parallelProcesses"])

            except IOError:
                self.messageBox("Error", "An error occured while attempting to load existing settings!")


        def saveButton_onclick(button):
            ### validation of the fields
            username = tb_username.get_edit_text()
            password = tb_password.get_edit_text()
            port = tb_port.get_edit_text()
            parallelProcesses = tb_parallel_processes.get_edit_text()

            if len(str(username)) < 3:
                self.messageBox("Input Error", "Username needs to have at least 3 charcters!")
                return
            if len(str(password)) < 3:
                self.messageBox("Input Error", "Password needs to have at least 3 charcters!")
                return
            if not port:
                self.messageBox("Input Error", "Port list cannot be left empty!")
                return
            if not parallelProcesses:
                self.messageBox("Input Error", "The number of parallel processes cannot be left empty!")
                return

            ports = port.split(",")
            for port in ports:
                if not utils.validatePort(port):
                    self.messageBox("Input Error", "The given port list is not valid!\nExpected syntax is port_1, port_2, ... where 0 < port_n < 65534 ")
                    return
            if not utils.validateParalellProcessNumber(parallelProcesses):
                self.messageBox("Input Error", "The given number of parallel processes is not valid!\nExpected values are between 0 - 25. ")
                return

            #### saving the settings to disk
            try:
                data = {}
                data["username"] = username
                data["password"] = password
                data["port"] = ports
                data["parallelProcesses"] = parallelProcesses
                with open("conf/directFetcher.conf", 'w') as file_handle:
                    file_handle.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("General Settings", "Settings have been saved succesfull!")
            except IOError:
                self.messageBox("General Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")

        saveButton = self.menu_button(u'Save', saveButton_onclick)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), helps, urwid.Divider(), tb_username, tb_password, tb_port, tb_parallel_processes, urwid.Divider(), saveButton, cancel_button]))
        load_settings()

    def directFetcher_commandSettings_dialog(self, button):
        caption = urwid.Text(('standoutLabel', u'Direct Mode > Commands'))
        helps = urwid.Text([u'In this section you can manually enter the commands you would like to execute on your devices based on their device group. A default set of commands are provided, but they can be edited either in this menu or in the "commands" folder of the tool. Note: The devices are grouped together based on the type of commands that need to be executed on them.'])

        MX = self.menu_button(u'MX/vMX/M/T/ACX/PTX device group', self.directFetcher_MX_dialog)
        SRX = self.menu_button(u'SRX/vSRX device group', self.directFetcher_SRX_dialog)
        QFX = self.menu_button(u'QFX/EX device group', self.directFetcher_QFX_dialog)

        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), helps, urwid.Divider(), MX, SRX, QFX, cancel_button]))

    def directFetcher_MX_dialog(self, button):

        caption = urwid.Text(('standoutLabel', u'Direct Mode > Commands > MX/vMX/M/T/ACX/PTX device group'))
        helps = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands = urwid.Edit(('textbox', u"Commands :\n"))
        def load_settings():
            try:
                settings = None
                string = ""
                with open('commands/MX_12.txt') as data_file:
                    settings = json.load(data_file)
                for i in xrange(len(settings["commandList"])-1):
                    string += settings["commandList"][i] + ","
                string += settings["commandList"][-1]
                tb_commands.set_edit_text(string)


            except IOError:
                self.messageBox("Error", "An error occured while attempting to load existing commands!")



        def saveButton_onclick(button):
            ### validation of the fields
            commands = tb_commands.get_edit_text()
            command_lines = commands.split(",")

            for i in xrange(len(command_lines)):
                command_lines[i] = command_lines[i].strip()
                if len(str(command_lines[i])) < 4:
                    self.messageBox("Input Error", "Command should have at least 4 charcters!")
                    return
                if (command_lines[i].split(" ", 1)[0] == 'request') and (command_lines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(command_lines[i]))
                    return


            #### saving the settings to disk
            try:
                data = {}

                data["commandList"] = command_lines

                with open("commands/MX_12.txt", 'w') as file_handle:
                    file_handle.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfully!")
            except IOError:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/MX_12.txt")

        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), helps, urwid.Divider(), tb_commands, urwid.Divider(), saveButton, cancel_button]))
        load_settings()

    def directFetcher_SRX_dialog(self, button):

        caption = urwid.Text(('standoutLabel', u'Direct Mode > Commands > SRX/vSRX device group'))
        helps = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands = urwid.Edit(('textbox', u"Commands :\n"))
        def load_settings():
            try:
                settings = None
                string = ""
                with open('commands/SRX_12.txt') as data_file:
                    settings = json.load(data_file)
                for i in xrange(len(settings["commandList"])-1):
                    string += settings["commandList"][i] + ","
                string += settings["commandList"][-1]
                tb_commands.set_edit_text(string)


            except IOError:
                self.messageBox("Error", "An error occured while attempting to load existing commands!")



        def saveButton_onclick(button):
            ### validation of the fields
            commands = tb_commands.get_edit_text()
            command_lines = commands.split(",")

            for i in xrange(len(command_lines)):
                command_lines[i] = command_lines[i].strip()
                if len(str(command_lines[i])) < 4:
                    self.messageBox("Input Error", "Command should have at least 4 charcters!")
                    return
                if (command_lines[i].split(" ", 1)[0] == 'request') and (command_lines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(command_lines[i]))
                    return


            #### saving the settings to disk
            try:
                data = {}

                data["commandList"] = command_lines

                with open("commands/SRX_12.txt", 'w') as file_handle:
                    file_handle.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfully!")
            except IOError:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/SRX_12.txt")

        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), helps, urwid.Divider(), tb_commands, urwid.Divider(), saveButton, cancel_button]))
        load_settings()

    def directFetcher_QFX_dialog(self, button):

        caption = urwid.Text(('standoutLabel', u'Direct Mode > Commands > QFX/EX device group'))
        helps = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands = urwid.Edit(('textbox', u"Commands :\n"))
        def load_settings():
            try:
                settings = None
                string = ""
                with open('commands/QFX_12.txt') as data_file:
                    settings = json.load(data_file)
                for i in xrange(len(settings["commandList"])-1):
                    string += settings["commandList"][i] + ","
                string += settings["commandList"][-1]
                tb_commands.set_edit_text(string)


            except IOError:
                self.messageBox("Error", "An error occured while attempting to load existing commands!")



        def saveButton_onclick(button):
            ### validation of the fields
            commands = tb_commands.get_edit_text()
            command_lines = commands.split(",")

            for i in xrange(len(command_lines)):
                command_lines[i] = command_lines[i].strip()
                if len(str(command_lines[i])) < 4:
                    self.messageBox("Input Error", "Command should have at least 4 charcters!")
                    return
                if (command_lines[i].split(" ", 1)[0] == 'request') and (command_lines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(command_lines[i]))
                    return


            #### saving the settings to disk
            try:
                data = {}

                data["commandList"] = command_lines

                with open("commands/QFX_12.txt", 'w') as file_handle:
                    file_handle.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfully!")
            except IOError:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/QFX_12.txt")

        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancel_button = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption, urwid.Divider(), helps, urwid.Divider(), tb_commands, urwid.Divider(), saveButton, cancel_button]))
        load_settings()




    # direct mode > verify  | creates a DirectFetcher object and attempts to load the inputs
    def directFetcher_verify(self, button):
        caption_label = urwid.Text(('standoutLabel', "Direct Mode > Verifying Inputs"))
        message_label = urwid.Text([""])
        button = self.menu_button(u'OK', self.exit_window)

        # creation of tool object
        direct = DirectFetcher("IB")
        (result, message) = direct.LoadInputFile()
        message_label.set_text(message + "\n")
        dialog = self.top.message_box(urwid.Pile([caption_label, urwid.Divider(), message_label, urwid.Divider(), button]))
