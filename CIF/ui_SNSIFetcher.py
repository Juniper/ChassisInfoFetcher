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

import urwid
import json
import utils
from SNSIFetcher import SNSIFetcher
from urlparse import urlparse
from ui_dialog import ui_dialog
import utils


class ui_SNSIFetcher(ui_dialog):

    # full mode main dialog
    def ShowDialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Junos Space | SNSI Mode'))
        help = urwid.Text([u'In SNSI mode the tool connects to Junos Space, retrieves the iJMB files collected by Junos Space and extracts the needed chassis information. Since this mode works with the iJMB files, in the command section, the necessary attachment files need to be specified, rather than regular commands.'])
        generalSettings = self.menu_button(u'Settings', self.SNSIFetcher_generalSettings_dialog)
        fetchInstallBase = self.menu_button(u'Fetch Install Base information', self.SNSIFetcher_IB)
        fetchASdeliverable = self.menu_button(u'Fetch information for Advanced Service deliverables', self.SNSIFetcher_AS)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings, fetchInstallBase, fetchASdeliverable, cancelButton]))


    def SNSIFetcher_IB(self,button):
        caption = urwid.Text(('standoutLabel',u'Direct Mode > Install Base'))

        verifyFileButton = self.menu_button(u'Verify Junos Space connectity', self.SNSIFetcher_verify)
        runButton = self.menu_button(u'Run', self.SNSIFetcherIB_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(), verifyFileButton, runButton,cancelButton]))

    def SNSIFetcher_AS(self,button):
        caption = urwid.Text(('standoutLabel',u'Direct Mode > Advanced Service Deliverables'))

        commandSettings = self.menu_button(u'Commands', self.SNSIFetcher_commandSettings_dialog)
        verifyFileButton = self.menu_button(u'Verify Junos Space connectity', self.SNSIFetcher_verify)
        runButton = self.menu_button(u'Run', self.SNSIFetcherAS_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(), commandSettings, verifyFileButton, runButton,cancelButton]))

    # direct mode > run  | creates the DirectFetcher object and runs the appropiate console tool
    def SNSIFetcherIB_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("SNSIFetcherIB")

        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher

    def SNSIFetcherAS_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("SNSIFetcherAS")
        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher

    # full mode > general settings window
    def SNSIFetcher_generalSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Settings'))
        help = urwid.Text([u'Please fill in the default url / username / password for Junos Space API. If the number of specified processes are more than the devices that the tool collects information from, then the tool can create parallel sessions for all devices and complete execution faster (this uses up more resources on the machine running the tool).'])

        tb_username=urwid.Edit(('textbox', u"Junos Space Username :\n"))
        tb_password=urwid.Edit(('textbox', u"Junos Space Password :\n"),mask="*")
        tb_url=urwid.Edit(('textbox', u"Junos Space IP address :\n"))
        tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        def load_settings():
            try:
                settings=None
                with open('conf/SNSIFetcher.conf') as data_file:
                   settings = json.load(data_file)
                tb_username.set_edit_text(settings["username_js"])
                tb_password.set_edit_text(settings["password_js"])
                tb_url.set_edit_text(settings["url"])
                tb_parallelProcesses.set_edit_text(settings["parallelProcesses"])



            except:
                self.messageBox("Error", "An error occured while attempting to load existing settings!")



        def saveButton_onclick(button):
            ### validation of the fields
            username=tb_username.get_edit_text()
            password=tb_password.get_edit_text()
            url=tb_url.get_edit_text()

            parallelProcesses=tb_parallelProcesses.get_edit_text()

            if len(str(username)) < 3:
                self.messageBox("Input Error", "Junos Space Username needs to have at least 3 charcters!")
                return
            if len(str(password)) < 3:
                self.messageBox("Input Error", "Junos Space Password needs to have at least 3 charcters!")
                return
            if len(str(url)) == 0:
                self.messageBox("Input Error", "The Junos Space URL needs to have at least 3 charcters and begin with http:// or https:// !")
                return
            if len(str(parallelProcesses)) == 0:
                self.messageBox("Input Error", "The number of parallel processes cannot be left empty!")
                return

            if not utils.validateParalellProcessNumber(parallelProcesses):
                self.messageBox("Input Error", "The given number of parallel processes is not valid!\nExpected values are between 0 - 25. ")
                return

            if not utils.validateUrl(url):
                self.messageBox("Input Error", "The Junos Space URL needs to be a valid http/https URL.")
                return


            #### saving the settings to disk
            try:
                data={}
                data["username_js"]=username
                data["password_js"]=password
                data["url"]=url
                data["parallelProcesses"]=parallelProcesses
                with open("conf/SNSIFetcher.conf", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Settings", "Settings have been saved succesfull!")
            except:
                self.messageBox("Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")

        saveButton = self.menu_button(u'Save', saveButton_onclick)


        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_url,tb_username,tb_password, tb_parallelProcesses, urwid.Divider(),saveButton,cancelButton]))
        load_settings()

    def SNSIFetcher_commandSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Commands'))
        help = urwid.Text([u'Please specify the file names whose output you would like to extract. The names are specified in the help section.'])

        MX = self.menu_button(u'MX/vMX/M/T/ACX/PTX device group', self.SNSIFetcher_MX_dialog)
        SRX = self.menu_button(u'SRX/vSRX device group', self.SNSIFetcher_SRX_dialog)
        QFX = self.menu_button(u'QFX/EX device group', self.SNSIFetcher_QFX_dialog)
        helps = self.menu_button(u'Help', self.SNSIFetcher_help_dialog)

        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),MX,SRX,QFX,helps,cancelButton]))

    def SNSIFetcher_MX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Commands > MX/vMX/M/T/ACX/PTX device group'))
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))

        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/MX_3.txt') as data_file:
                   settings = json.load(data_file)
                for i in xrange(len(settings["commandList"])-1):
                    string += settings["commandList"][i] + ","
                string += settings["commandList"][-1]
                tb_commands.set_edit_text(string)


            except:
                self.messageBox("Error", "An error occured while attempting to load existing commands!")



        def saveButton_onclick(button):
            ### validation of the fields
            commands=tb_commands.get_edit_text()
            commandLines = commands.split(",")

            for i in xrange(len(commandLines)):
                commandLines[i] = commandLines[i].strip()
                if len(str(commandLines[i])) < 4:
                    self.messageBox("Input Error", "File name should have at least 4 charcters!")
                    return
                if (commandLines[i].split(" ", 1)[0] == "show"):
                    self.messageBox("Input Error", "Commands cannot be executed in this mode!")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') or (commandLines[i].split(" ", 1)[0] == 'restart'):
                    self.messageBox("Input Error", "Commands cannot be executed in this mode!")
                    return

            #### saving the settings to disk
            try:
                data={}
                data["commandList"]=commandLines

                with open("commands/MX_3.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("File names", "File names have been saved succesfull!")
            except:
                self.messageBox("File names > Error", "There were errors while attempting to save the file names to disk.\nPlease check permissions rights and/or locks for file: commands/MX_3.txt")

        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands, urwid.Divider(),saveButton,cancelButton]))
        load_settings()

    def SNSIFetcher_SRX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Commands > SRX/vSRX device group'))
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))

        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/SRX_3.txt') as data_file:
                   settings = json.load(data_file)
                for i in xrange(len(settings["commandList"])-1):
                    string += settings["commandList"][i] + ","
                string += settings["commandList"][-1]
                tb_commands.set_edit_text(string)


            except:
                self.messageBox("Error", "An error occured while attempting to load existing commands!")



        def saveButton_onclick(button):
            ### validation of the fields
            commands=tb_commands.get_edit_text()
            commandLines = commands.split(",")

            for i in xrange(len(commandLines)):
                commandLines[i] = commandLines[i].strip()
                if len(str(commandLines[i])) < 4:
                    self.messageBox("Input Error", "File name should have at least 4 charcters!")
                    return
                if (commandLines[i].split(" ", 1)[0] == "show"):
                    self.messageBox("Input Error", "Commands cannot be executed in this mode!")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') or (commandLines[i].split(" ", 1)[0] == 'restart'):
                    self.messageBox("Input Error", "Commands cannot be executed in this mode!")
                    return

            #### saving the settings to disk
            try:
                data={}
                data["commandList"]=commandLines

                with open("commands/SRX_3.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("File names", "File names have been saved succesfull!")
            except:
                self.messageBox("File names > Error", "There were errors while attempting to save the file names to disk.\nPlease check permissions rights and/or locks for file: commands/SRX_3.txt")

        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands, urwid.Divider(),saveButton,cancelButton]))
        load_settings()

    def SNSIFetcher_QFX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Commands > SRX/vSRX device group'))
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))

        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/QFX_3.txt') as data_file:
                   settings = json.load(data_file)
                for i in xrange(len(settings["commandList"])-1):
                    string += settings["commandList"][i] + ","
                string += settings["commandList"][-1]
                tb_commands.set_edit_text(string)


            except:
                self.messageBox("Error", "An error occured while attempting to load existing commands!")



        def saveButton_onclick(button):
            ### validation of the fields
            commands=tb_commands.get_edit_text()
            commandLines = commands.split(",")

            for i in xrange(len(commandLines)):
                commandLines[i] = commandLines[i].strip()
                if len(str(commandLines[i])) < 4:
                    self.messageBox("Input Error", "File name should have at least 4 charcters!")
                    return
                if (commandLines[i].split(" ", 1)[0] == "show"):
                    self.messageBox("Input Error", "Commands cannot be executed in this mode!")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') or (commandLines[i].split(" ", 1)[0] == 'restart'):
                    self.messageBox("Input Error", "Commands cannot be executed in this mode!")
                    return

            #### saving the settings to disk
            try:
                data={}
                data["commandList"]=commandLines

                with open("commands/QFX_3.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("File names", "File names have been saved succesfull!")
            except:
                self.messageBox("File names > Error", "There were errors while attempting to save the file names to disk.\nPlease check permissions rights and/or locks for file: commands/SRX_3.txt")

        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands, urwid.Divider(),saveButton,cancelButton]))
        load_settings()

    def SNSIFetcher_help_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Help'))
        help = urwid.Text([u'''Here you can find a mapping between the iJMB attachment files and the configuration information included in them:
            _AISESI.txt — Contains event support information; output of multiple Junos OS show commands
            _rsi.txt — Contains “request support information” of the device
            _cfg_xml.xml — Contains device configuration information in XML format (show configuration | display inheritance | display xml)
            _shd_xml.xml — Contains output of the “show chassis hardware” command in XML format
            _ver_xml.xml — Contains the hostname and version information about the software (including the software help files and AI-Scripts bundle) running on the device (show version)

            That is why in the command section of the Service Now Service Insight mode, the relevant files are specified and not actual commands (for example, include: _AISESI.txt, _cfg_xml, _shd_xml).'''])

        cancelButton = self.menu_button(u'Cancel', self.exit_window)
        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),cancelButton]))

    # SNSIFetcher mode > run  | creates the DirectFetcher object and runs the appropiate console tool
    def SNSIFetcher_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("SNSIFetcher")
        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher


    # SNSIFetcher mode > verify  | creates a DirectFetcher object and attempts to load the inputs
    def SNSIFetcher_verify(self,button):
        captionLabel = urwid.Text(('standoutLabel',"SNSI Mode > Verifying Junos Space connectity"))
        messageLabel = urwid.Text([""])
        button = self.menu_button(u'OK', self.exit_window)

        # creation of tool object
        df=SNSIFetcher("IB")
        (result,message)=df.LoadInputFile()
        messageLabel.set_text(message+"\n")
        dialog=self.top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))
