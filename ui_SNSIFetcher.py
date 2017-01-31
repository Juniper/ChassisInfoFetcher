# coding: utf-8
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
        commandSettings = self.menu_button(u'Commands', self.SNSIFetcher_commandSettings_dialog)
        verifyFileButton = self.menu_button(u'Verify Junos Space connectity', self.SNSIFetcher_verify)
        runButton = self.menu_button(u'Run', self.SNSIFetcher_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings, commandSettings, verifyFileButton, runButton,cancelButton]))
         


    # full mode > general settings window
    def SNSIFetcher_generalSettings_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'SNSI Mode > Settings')) 
        help = urwid.Text([u'Please fill in the default url / username / password for Junos Space API. If the number of specified processes are more than the devices that the tool collects information from, then the tool can create parallel sessions for all devices and complete execution faster (this uses up more resources on the machine running the tool).'])
        
        tb_username=urwid.Edit(('textbox', u"Junos Space Username :\n"))
        tb_password=urwid.Edit(('textbox', u"Junos Space Password :\n"),mask="*")
        tb_url=urwid.Edit(('textbox', u"Junos Space URL :\n"))
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
        df=SNSIFetcher()
        (result,message)=df.LoadInputFile()
        messageLabel.set_text(message+"\n")
        dialog=self.top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))
