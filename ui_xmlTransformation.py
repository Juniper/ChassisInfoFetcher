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
from xmlToPlainText import XMLToPlainText
from urlparse import urlparse
from ui_dialog import ui_dialog
import utils

class ui_xmlTransformation(ui_dialog):
   
             
    # direct mode main dialog
    def ShowDialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Transform XML')) 
        help = urwid.Text([u'The tool provides capability for xml to plain text and xml to set-format transformations.'])
        
        xmlToPlainText = self.menu_button(u'XML to plain text', self.xmlToPlainText_dialog)
        #xmlToSet = self.menu_button(u'XML to set', self.xmlToSet_dialog)

        cancelButton = self.menu_button(u'Cancel', self.exit_window)
        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),xmlToPlainText, cancelButton]))

        #top.open_box(urwid.Filler(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings,verifyFileButton, runButton,cancelButton])))



    # direct mode > run  | creates the DirectFetcher object and runs the appropiate console tool
    def xmlToPlainText_run(self,button):
        with open("execute.task", 'w') as f:
            f.write("XMLToPlainText")
        self.exit_program(None)   #closing the graphical interface to run the DirectFetcher

      
    # direct mode > general settings window
    def xmlToPlainText_dialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Transform XML > XML to plain text')) 
        help = urwid.Text([u'Please specify the input file which is in xml format and the name of the output file.'])

        
        tb_username=urwid.Edit(('textbox', u"Input :\n"))
        tb_password=urwid.Edit(('textbox', u"Output :\n"))
        runButton = self.menu_button(u'Run', self.xmlToPlainText_run)
        cancelButton = self.menu_button(u'Cancel', self.exit_window)

        ### loading previouse settings
        def load_settings():
            try:
                settings=None
                with open('conf/xmlToPlainText.conf') as data_file:    
                   settings = json.load(data_file)
                tb_username.set_edit_text(settings["input"])
                tb_password.set_edit_text(settings["output"])

            except:
                self.messageBox("Error", "An error occured while attempting to load existing settings!")
    

        def saveButton_onclick(button):
            ### validation of the fields        
            username=tb_username.get_edit_text()
            password=tb_password.get_edit_text()

            
            if len(str(username)) < 3:
                self.messageBox("Input Error", "Username needs to have at least 3 charcters!")
                return
            if len(str(password)) < 3:
                self.messageBox("Input Error", "Password needs to have at least 3 charcters!")
                return

            #### saving the settings to disk
            try:
                data={}
                data["input"]=username
                data["output"]=password

                with open("conf/xmlToPlainText.conf", 'w') as f:
                    f.write(json.dumps(data, indent=4, sort_keys=True))

                self.messageBox("General Settings", "Settings have been saved succesfull!")
            except:
                self.messageBox("General Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                    
        saveButton = self.menu_button(u'Save', saveButton_onclick)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_username,tb_password,urwid.Divider(),saveButton,runButton,cancelButton]))
        load_settings()

