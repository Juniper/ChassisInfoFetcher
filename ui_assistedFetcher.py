
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
 ********************************************************************************
 * Project GIT  :  https://git.juniper.net/asmeureanu/ChassisInfoFetcher
 ********************************************************************************
"""

import urwid
import json
import utils
from assistedFetcher import AssistedFetcher
from urlparse import urlparse
from ui_dialog import ui_dialog
import utils


class ui_assistedFetcher(ui_dialog):
    # assisted mode main dialog
    def ShowDialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Junos Space | Assisted Mode')) 
        help = urwid.Text([u'In the assisted mode the tool will retrieve the device list from Junos Space and proceed to connect to them in parallel in order to retrieve the chassis information.'])
        
        generalSettings = self.menu_button(u'Settings', self.assistedFetcher_generalSettings_dialog)
        commandSettings = self.menu_button(u'Commands', self.assistedFetcher_commandSettings_dialog)
        verifyFileButton = self.menu_button(u'Verify Junos Space connectity', self.assistedFetcher_verify)
        runButton = self.menu_button(u'Run', self.assistedFetcher_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings, commandSettings, verifyFileButton, runButton,cancelButton]))
          
             
    
    # assisted mode > verify  | creates a DirectFetcher object and attempts to load the inputs
    def assistedFetcher_verify(self,button):
        captionLabel = urwid.Text(('standoutLabel',"Assisted Mode > Verifying Junos Space connectity"))
        messageLabel = urwid.Text([""])
        button = self.menu_button(u'OK', self.exit_window)
       
        # creation of tool object
        df=AssistedFetcher()
        (result,message)=df.LoadInputFile()
        messageLabel.set_text(message+"\n")
        dialog=self.top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))

    # assisted mode > general settings window
    def assistedFetcher_generalSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Assisted Mode > Settings')) 
        help = urwid.Text([u'Please fill in the default username / password for SSH connectiy to the devices and Junos Space API url / username / password. If the number of specified processes are more than the devices that the tool collects information from, then the tool can create parallel sessions for all devices and complete execution faster (this uses up more resources on the machine running the tool).'])
        
        tb_username=urwid.Edit(('textbox', u"Junos Space Username :\n"))
        tb_password=urwid.Edit(('textbox', u"Junos Space Password :\n"),mask="*")
        tb_url=urwid.Edit(('textbox', u"Junos Space URL :\n"))
        tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
        tb_username_ssh=urwid.Edit(('textbox', u"Device SSH Username :\n"))
        tb_password_ssh=urwid.Edit(('textbox', u"Device SSH Password :\n"),mask="*")
        tb_port=urwid.Edit(('textbox', u"Device SSH Port List comma separated (e.g.: 22,222,2222) :\n"))
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        def load_settings():
            try:
                settings=None
                with open('conf/assistedFetcher.conf') as data_file:    
                   settings = json.load(data_file)
                tb_username.set_edit_text(settings["js_username"])
                tb_password.set_edit_text(settings["js_password"])
                tb_username_ssh.set_edit_text(settings["device_ssh_username"])
                tb_password_ssh.set_edit_text(settings["device_ssh_password"])
                tb_url.set_edit_text(settings["url"])
                tb_parallelProcesses.set_edit_text(settings["parallelProcesses"])
               
                ### loading the ports list from the json array format needs flattening
                str_port=""
                for port in settings["port"]:
                    str_port+=port+","
                str_port=str_port.strip(",")
                tb_port.set_edit_text(str_port)

            except:
                self.messageBox("Error", "An error occured while attempting to load existing settings!")



        def saveButton_onclick(button):
            ### validation of the fields        
            username=tb_username.get_edit_text()
            password=tb_password.get_edit_text()
            username_ssh=tb_username_ssh.get_edit_text()
            password_ssh=tb_password_ssh.get_edit_text()
            url=tb_url.get_edit_text()
            port=tb_port.get_edit_text()

            parallelProcesses=tb_parallelProcesses.get_edit_text()
            
            if len(str(username)) < 3:
                self.messageBox("Input Error", "Junos Space Username needs to have at least 3 charcters!")
                return
            if len(str(password)) < 3:
                self.messageBox("Input Error", "Junos Space Password needs to have at least 3 charcters!")
                return
            if len(str(username_ssh)) < 3:
                self.messageBox("Input Error", "Device SSH Username needs to have at least 3 charcters!")
                return
            if len(str(password_ssh)) < 3:
                self.messageBox("Input Error", "Device SSH Password needs to have at least 3 charcters!")
                return
            if len(str(url)) == 0:
                self.messageBox("Input Error", "The Junos Space URL needs to have at least 3 charcters and begin with http:// or https:// !")
                return
            if len(str(parallelProcesses)) == 0:
                self.messageBox("Input Error", "The number of parallel processes cannot be left empty!")
                return
            if len(str(port)) == 0:
                self.messageBox("Input Error", "Port list cannot be left empty!")
                return
        
            if not utils.validateParalellProcessNumber(parallelProcesses):
                self.messageBox("Input Error", "The given number of parallel processes is not valid!\nExpected values are between 0 - 25. ")
                return
            
            if not utils.validateUrl(url):
                self.messageBox("Input Error", "The Junos Space URL needs to be a valid http/https URL.")
                return
            
            ports = port.split(",")
            for p in ports:
                if not utils.validatePort(p):
                    self.messageBox("Input Error", "The given port list is not valid!\nExpected syntax is port_1, port_2, ... where 0 < port_n < 65534 ")
                    return
        
            #### saving the settings to disk
            try:
                data={}
                data["js_username"]=username
                data["js_password"]=password
                data["device_ssh_username"]=username_ssh
                data["device_ssh_password"]=password_ssh
                data["url"]=url
                data["parallelProcesses"]=parallelProcesses
                data["port"]=ports
                with open("conf/assistedFetcher.conf", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Settings", "Settings have been saved succesfull!")
            except:
                self.messageBox("Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                    
        saveButton = self.menu_button(u'Save',  saveButton_onclick)


        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_url,tb_username,tb_password, tb_parallelProcesses,tb_username_ssh,tb_password_ssh,tb_port, urwid.Divider(),saveButton,cancelButton]))
        load_settings()

    def assistedFetcher_commandSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Assisted Mode > Commands')) 
        help = urwid.Text([u'In this section you can manually enter the commands you would like to execute on your devices based on their device group. A default set of commands are provided, but they can be edited either in this menu or in the "commands" folder of the tool. Note: The devices are grouped together based on the type of commands that need to be executed on them.'])
        
        MX = self.menu_button(u'MX/vMX/M/T/ACX/PTX device group', self.assistedFetcher_MX_dialog)
        SRX = self.menu_button(u'SRX/vSRX device group', self.assistedFetcher_SRX_dialog)
        QFX = self.menu_button(u'QFX/EX device group', self.assistedFetcher_QFX_dialog)
      
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),MX,SRX,QFX,cancelButton]))


    def assistedFetcher_MX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'Assisted Mode > Commands > MX/vMX/M/T/ACX/PTX device group')) 
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))
        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/MX_12.txt') as data_file:    
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
                    self.messageBox("Input Error", "Command should have at least 4 charcters!")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') and (commandLines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                    return
            
        
            #### saving the settings to disk
            try:
                data={}

                data["commandList"]=commandLines

                with open("commands/MX_12.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfull!")
            except:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/MX_12.txt")
                    
        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)


        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands, urwid.Divider(),saveButton,cancelButton]))
        cancelButton = self.menu_button(u'Cancel', self.exit_window)
        load_settings()    

    def assistedFetcher_SRX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'Assisted Mode > Commands > SRX/vSRX device group')) 
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))
        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/SRX_12.txt') as data_file:    
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
                    self.messageBox("Input Error", "Command should have at least 4 charcters!")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') and (commandLines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                    return
            
        
            #### saving the settings to disk
            try:
                data={}

                data["commandList"]=commandLines

                with open("commands/SRX_12.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfull!")
            except:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/SRX_12.txt")
                    
        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)


        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands, urwid.Divider(),saveButton,cancelButton]))
        cancelButton = self.menu_button(u'Cancel', self.exit_window)
        load_settings()   

    def assistedFetcher_QFX_dialog(self,button):

        caption = urwid.Text(('standoutLabel',u'Assisted Mode > Commands > QFX/EX device group')) 
        help = urwid.Text([u'In this menu you can edit the commands that are going to be automatically executed on the devices from this device group. Only "show" commands and the "request support information" command are allowed to be entered. The tool will not execute any other type of command.'])
        tb_commands=urwid.Edit(('textbox', u"Commands :\n"))
        def load_settings():
            try:
                settings=None
                string = ""
                with open('commands/QFX_12.txt') as data_file:    
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
                    self.messageBox("Input Error", "Command should have at least 4 charcters!")
                    return
                if (commandLines[i].split(" ", 1)[0] == 'request') and (commandLines[i] != 'request support information'):
                    self.messageBox("Input Error", "The following command is not allowed: %s"%(commandLines[i]))
                    return
            
        
            #### saving the settings to disk
            try:
                data={}

                data["commandList"]=commandLines

                with open("commands/QFX_12.txt", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("Commands", "Commands have been saved succesfull!")
            except:
                self.messageBox("Commands > Error", "There were errors while attempting to save the commands to disk.\nPlease check permissions rights and/or locks for file: commands/QFX_12.txt")
                    
        saveButton = self.menu_button(u'Save', saveButton_onclick)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)


        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_commands, urwid.Divider(),saveButton,cancelButton]))
        cancelButton = self.menu_button(u'Cancel', self.exit_window)
        load_settings()    



    # assisted mode > run  | creates the DirectFetcher object and runs the appropiate console tool
    def assistedFetcher_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("AssistedFetcher")
        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher
