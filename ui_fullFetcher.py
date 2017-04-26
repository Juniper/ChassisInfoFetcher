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
from fullFetcher import FullFetcher
from urlparse import urlparse
from ui_dialog import ui_dialog
import utils


class ui_fullFetcher(ui_dialog):

    # full mode main dialog
    def ShowDialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Junos Space | Full Mode')) 
        help = urwid.Text([u'In full mode the tool retrieves the device list from Junos Space and instructs Junos space to connect to all devices to retrieve the information necessary for the Advanced Services deliverable. For successful execution, please enter the necessary info in the Settings menu.'])
        generalSettings = self.menu_button(u'Settings', self.fullFetcher_generalSettings_dialog)

        fetchInstallBase = self.menu_button(u'Fetch Install Base information', self.fullFetcher_IB)
        fetchASdeliverable = self.menu_button(u'Fetch information for Advanced Service deliverables', self.fullFetcher_AS)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings, fetchInstallBase, fetchASdeliverable, cancelButton]))
         


    def fullFetcher_IB(self,button):
        caption = urwid.Text(('standoutLabel',u'Direct Mode > Install Base'))

        verifyFileButton = self.menu_button(u'Verify Junos Space connectity', self.fullFetcher_verify)
        runButton = self.menu_button(u'Run', self.fullFetcherIB_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(), verifyFileButton, runButton,cancelButton]))

    def fullFetcher_AS(self,button):
        caption = urwid.Text(('standoutLabel',u'Direct Mode > Advanced Service Deliverables'))

        commandSettings = self.menu_button(u'Commands', self.fullFetcher_commandSettings_dialog)
        verifyFileButton = self.menu_button(u'Verify Junos Space connectity', self.fullFetcher_verify)
        runButton = self.menu_button(u'Run', self.fullFetcherAS_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(), commandSettings, verifyFileButton, runButton,cancelButton]))

    # direct mode > run  | creates the DirectFetcher object and runs the appropiate console tool
    def fullFetcherIB_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("FullFetcherIB")

        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher

    def fullFetcherAS_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("FullFetcherAS")
        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher

    # full mode > general settings window
    def fullFetcher_generalSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Full Mode > Settings')) 
        help = urwid.Text([u'Please fill in the default url / username / password for Junos Space API. If the number of specified processes are more than the devices that the tool collects information from, then the tool can create parallel sessions for all devices and complete execution faster (this uses up more resources on the machine running the tool).'])
        
        tb_username=urwid.Edit(('textbox', u"Junos Space Username :\n"))
        tb_password=urwid.Edit(('textbox', u"Junos Space Password :\n"),mask="*")
        tb_url=urwid.Edit(('textbox', u"Junos Space URL :\n"))
        tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        def load_settings():
            try:
                settings=None
                with open('conf/fullFetcher.conf') as data_file:    
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
                with open("conf/fullFetcher.conf", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Settings", "Settings have been saved succesfull!")
            except:
                self.messageBox("Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                    
        saveButton = self.menu_button(u'Save', saveButton_onclick)


        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_url,tb_username,tb_password, tb_parallelProcesses, urwid.Divider(),saveButton,cancelButton]))
        load_settings()

    def fullFetcher_commandSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Full Mode > Commands')) 
        help = urwid.Text([u'In this section you can manually enter the commands you would like to execute on your devices based on their device group. A default set of commands are provided, but they can be edited either in this menu or in the "commands" folder of the tool. Note: The devices are grouped together based on the type of commands that need to be executed on them.'])

        MX = self.menu_button(u'MX/vMX/M/T/ACX/PTX device group', self.fullFetcher_MX_dialog)
        SRX = self.menu_button(u'SRX/vSRX device group', self.fullFetcher_SRX_dialog)
        QFX = self.menu_button(u'QFX/EX device group', self.fullFetcher_QFX_dialog)
        
      
        cancelButton = self.menu_button(u'Cancel', self.exit_window)



        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),MX,SRX,QFX,cancelButton]))

    def fullFetcher_MX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'Full Mode > Commands > MX/vMX/M/T/ACX/PTX device group')) 
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))

        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/MX_4.txt') as data_file:    
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
                commandLines[i]=commandLines[i].strip()
                if len(str(commandLines[i])) < 4:
                    self.messageBox("Input Error", "Command should have at least 4 charcters! (Check for trailing commas")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') and (commandLines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                    return
                if (commandLines[i].split("|", 1)[-1].strip() == 'display xml'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                    return
        
            #### saving the settings to disk
            try:
                data={}
                #for i in xrange(len(commandLines)):
                data["commandList"]=commandLines

                with open("commands/MX_4.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfully!")
            except:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/MX_4.txt")
                    
        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)
        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands,urwid.Divider(),saveButton,cancelButton])) 
        load_settings()   


    def fullFetcher_SRX_dialog(self,button):

            caption = urwid.Text(('standoutLabel',u'Full Mode > Commands')) 
            help = urwid.Text([u'In this you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
            tb_commands=urwid.Edit(('textbox', u"Commands :\n"))
            def load_settings():
                try:
                    settings=None
                    string = ""
                    with open('commands/SRX_4.txt') as data_file:    
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
                    commandLines[i]=commandLines[i].strip()
                    if len(str(commandLines[i])) < 4:
                        self.messageBox("Input Error", "Command should have at least 4 charcters! (Check for trailing commas")
                        return
                    if (commandLines[i].split(" ", 1)[0] == 'request') and (commandLines[i] != 'request support information'):
                        self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                        return
                    if (commandLines[i].split("|", 1)[-1].strip() == 'display xml'):
                        self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                        return
            
                #### saving the settings to disk
                try:
                    data={}
                    #for i in xrange(len(commandLines)):
                    data["commandList"]=commandLines

                    with open("commands/SRX_4.txt", 'w') as f:
                        f.write(json.dumps(data, indent=4, sort_keys=True))

                    self.messageBox("Commands", "Commands have been saved succesfull!")
                except:
                    self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: fullFetcherCommands.txt")
                        
            saveButton = self.menu_button(u'Save', saveButton_onclick)
            cancelButton = self.menu_button(u'Cancel', self.exit_window)
            self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands,urwid.Divider(),saveButton,cancelButton])) 
            load_settings()  

    def fullFetcher_QFX_dialog(self,button):

            caption = urwid.Text(('standoutLabel',u'Full Mode > Commands')) 
            help = urwid.Text([u'In this you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
            tb_commands=urwid.Edit(('textbox', u"Commands :\n"))
            def load_settings():
                try:
                    settings=None
                    string = ""
                    with open('commands/QFX_4.txt') as data_file:    
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
                    commandLines[i]=commandLines[i].strip()
                    if len(str(commandLines[i])) < 4:
                        self.messageBox("Input Error", "Command should have at least 4 charcters! (Check for trailing commas")
                        return
                    if (commandLines[i].split(" ", 1)[0] == 'request') and (commandLines[i] != 'request support information'):
                        self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                        return
                    if (commandLines[i].split("|", 1)[-1].strip() == 'display xml'):
                        self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                        return
            
                #### saving the settings to disk
                try:
                    data={}
                    #for i in xrange(len(commandLines)):
                    data["commandList"]=commandLines

                    with open("commands/QFX_4.txt", 'w') as f:
                        f.write(json.dumps(data, indent=4, sort_keys=True))

                    self.messageBox("Commands", "Commands have been saved succesfull!")
                except:
                    self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: fullFetcherCommands.txt")
                        
            saveButton = self.menu_button(u'Save', saveButton_onclick)
            cancelButton = self.menu_button(u'Cancel', self.exit_window)
            self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands,urwid.Divider(),saveButton,cancelButton])) 
            load_settings()  




    # assisted mode > verify  | creates a DirectFetcher object and attempts to load the inputs
    def fullFetcher_verify(self,button):
        captionLabel = urwid.Text(('standoutLabel',"Full Mode > Verifying Junos Space connectity"))
        messageLabel = urwid.Text([""])
        button = self.menu_button(u'OK', self.exit_window)
       
        # creation of tool object
        df=FullFetcher("IB")
        (result,message)=df.LoadInputFile()
        messageLabel.set_text(message+"\n")
        dialog=self.top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))

