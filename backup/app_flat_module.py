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
from urlparse import urlparse

from directFetcher import DirectFetcher
from assistedFetcher import AssistedFetcher
from fullFetcher import FullFetcher

task = None 

def validateParalellProcessNumber(string_parallelProcesses):
    try:
        nr= int(string_parallelProcesses)
        if nr < 0 or nr > 25 :
            return False
        return True
    except:
        return False

def validatePort(string_port):
    try:
        port= int(string_port)
        if port < 0 or port > 65534 :
            return False
        return True
    except:
        return False

def validateUrl(string_url):
    try:
         urlparse(string_url)
         return True
    except:
        return False


def messageBox(caption,message):
    captionLabel = urwid.Text(('standoutLabel',caption))
    messageLabel = urwid.Text([message])
    button = menu_button(u'OK', exit_window)
    top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))
   



##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

# full mode main dialog
def fullFetcher_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Junos Space | Full Mode')) 
    help = urwid.Text([u'In the full mode the tool will retrieve the device list from Junos Space and instruct Junos space to connect to all devices to retrieve the chassis information.'])
    generalSettings = menu_button(u'Settings', fullFetcher_generalSettings_dialog)
    verifyFileButton = menu_button(u'Verify Junos Space connectity', fullFetcher_verify)
    runButton = menu_button(u'Run', fullFetcher_run)
    cancelButton = menu_button(u'Cancel', exit_window)

    top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings,verifyFileButton, runButton,cancelButton]))
     


# full mode > general settings window
def fullFetcher_generalSettings_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Full Mode > Settings')) 
    help = urwid.Text([u'Please fill in the default url / username / password for Junos Space API'])
    
    tb_username=urwid.Edit(('textbox', u"Junos Space Username :\n"))
    tb_password=urwid.Edit(('textbox', u"Junos Space Password :\n"),mask="*")
    tb_url=urwid.Edit(('textbox', u"Junos Space URL :\n"))
    tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
    cancelButton = menu_button(u'Cancel', exit_window)

    def load_settings():
        try:
            settings=None
            with open('fullFetcher.conf') as data_file:    
               settings = json.load(data_file)
            tb_username.set_edit_text(settings["username_js"])
            tb_password.set_edit_text(settings["password_js"])           
            tb_url.set_edit_text(settings["url"])
            tb_parallelProcesses.set_edit_text(settings["parallelProcesses"])
           
         

        except:
            messageBox("Error", "An error occured while attempting to load existing settings!")



    def saveButton_onclick(button):
        ### validation of the fields        
        username=tb_username.get_edit_text()
        password=tb_password.get_edit_text()
        url=tb_url.get_edit_text()
  
        parallelProcesses=tb_parallelProcesses.get_edit_text()
        
        if len(str(username)) < 3:
            messageBox("Input Error", "Junos Space Username needs to have at least 3 charcters!")
            return
        if len(str(password)) < 3:
            messageBox("Input Error", "Junos Space Password needs to have at least 3 charcters!")
            return   
        if len(str(url)) == 0:
            messageBox("Input Error", "The Junos Space URL needs to have at least 3 charcters and begin with http:// or https:// !")
            return
        if len(str(parallelProcesses)) == 0:
            messageBox("Input Error", "The number of parallel processes cannot be left empty!")
            return
     
        if not validateParalellProcessNumber(parallelProcesses):
            messageBox("Input Error", "The given number of parallel processes is not valid!\nExpected values are between 0 - 25. ")
            return
        
        if not validateUrl(url):
            messageBox("Input Error", "The Junos Space URL needs to be a valid http/https URL.")
            return
        
    
        #### saving the settings to disk
        try:
            data={}
            data["username_js"]=username
            data["password_js"]=password
            data["url"]=url
            data["parallelProcesses"]=parallelProcesses
            with open("fullFetcher.conf", 'w') as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))

            messageBox("Settings", "Settings have been saved succesfull!")
        except:
            messageBox("Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                
    saveButton = menu_button(u'Save', saveButton_onclick)


    top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_url,tb_username,tb_password, tb_parallelProcesses, urwid.Divider(),saveButton,cancelButton]))
    load_settings()

# assisted mode > run  | creates the DirectFetcher object and runs the appropiate console tool
def fullFetcher_run(button):
    global task
    task = "FullFetcher"
    exit_program(None)   #closing the graphical interface to run the DirectFetcher


# assisted mode > verify  | creates a DirectFetcher object and attempts to load the inputs
def fullFetcher_verify(button):
    captionLabel = urwid.Text(('standoutLabel',"Full Mode > Verifying Junos Space connectity"))
    messageLabel = urwid.Text([""])
    button = menu_button(u'OK', exit_window)
   
    # creation of tool object
    df=DirectFetcher()
    (result,message)=df.LoadInputFile()
    messageLabel.set_text(message+"\n")
    dialog=top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))

##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

# assisted mode > verify  | creates a DirectFetcher object and attempts to load the inputs
def assistedFetcher_verify(button):
    captionLabel = urwid.Text(('standoutLabel',"Assisted Mode > Verifying Junos Space connectity"))
    messageLabel = urwid.Text([""])
    button = menu_button(u'OK', exit_window)
   
    # creation of tool object
    df=DirectFetcher()
    (result,message)=df.LoadInputFile()
    messageLabel.set_text(message+"\n")
    dialog=top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))

# assisted mode > general settings window
def assistedFetcher_generalSettings_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Assisted Mode > Settings')) 
    help = urwid.Text([u'Please fill in the default username / password for SSH connectiy to the devices and Junos Space API url / username / password.'])
    
    tb_username=urwid.Edit(('textbox', u"Junos Space Username :\n"))
    tb_password=urwid.Edit(('textbox', u"Junos Space Password :\n"),mask="*")
    tb_url=urwid.Edit(('textbox', u"Junos Space URL :\n"))
    tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
    tb_username_ssh=urwid.Edit(('textbox', u"Device SSH Username :\n"))
    tb_password_ssh=urwid.Edit(('textbox', u"Device SSH Password :\n"),mask="*")
    tb_port=urwid.Edit(('textbox', u"Device SSH Port List :\n"))
    cancelButton = menu_button(u'Cancel', exit_window)

    def load_settings():
        try:
            settings=None
            with open('assistedFetcher.conf') as data_file:    
               settings = json.load(data_file)
            tb_username.set_edit_text(settings["username_js"])
            tb_password.set_edit_text(settings["password_js"])
            tb_username_ssh.set_edit_text(settings["username_ssh"])
            tb_password_ssh.set_edit_text(settings["password_ssh"])
            tb_url.set_edit_text(settings["url"])
            tb_parallelProcesses.set_edit_text(settings["parallelProcesses"])
           
            ### loading the ports list from the json array format needs flattening
            str_port=""
            for port in settings["port"]:
                str_port+=port+","
            str_port=str_port.strip(",")
            tb_port.set_edit_text(str_port)

        except:
            messageBox("Error", "An error occured while attempting to load existing settings!")



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
            messageBox("Input Error", "Junos Space Username needs to have at least 3 charcters!")
            return
        if len(str(password)) < 3:
            messageBox("Input Error", "Junos Space Password needs to have at least 3 charcters!")
            return
        if len(str(username_ssh)) < 3:
            messageBox("Input Error", "Device SSH Username needs to have at least 3 charcters!")
            return
        if len(str(password_ssh)) < 3:
            messageBox("Input Error", "Device SSH Password needs to have at least 3 charcters!")
            return
        if len(str(url)) == 0:
            messageBox("Input Error", "The Junos Space URL needs to have at least 3 charcters and begin with http:// or https:// !")
            return
        if len(str(parallelProcesses)) == 0:
            messageBox("Input Error", "The number of parallel processes cannot be left empty!")
            return
        if len(str(port)) == 0:
            messageBox("Input Error", "Port list cannot be left empty!")
            return
    
        if not validateParalellProcessNumber(parallelProcesses):
            messageBox("Input Error", "The given number of parallel processes is not valid!\nExpected values are between 0 - 25. ")
            return
        
        if not validateUrl(url):
            messageBox("Input Error", "The Junos Space URL needs to be a valid http/https URL.")
            return
        
        ports = port.split(",")
        for p in ports:
            if not validatePort(p):
                messageBox("Input Error", "The given port list is not valid!\nExpected syntax is port_1, port_2, ... where 0 < port_n < 65534 ")
                return
    
        #### saving the settings to disk
        try:
            data={}
            data["username_js"]=username
            data["password_js"]=password
            data["username_ssh"]=username_ssh
            data["password_ssh"]=password_ssh
            data["url"]=url
            data["parallelProcesses"]=parallelProcesses
            data["port"]=ports
            with open("assistedFetcher.conf", 'w') as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))

            messageBox("Settings", "Settings have been saved succesfull!")
        except:
            messageBox("Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                
    saveButton = menu_button(u'Save', saveButton_onclick)


    top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_url,tb_username,tb_password, tb_parallelProcesses,tb_username_ssh,tb_password_ssh,tb_port, urwid.Divider(),saveButton,cancelButton]))
    load_settings()

# assisted mode > run  | creates the DirectFetcher object and runs the appropiate console tool
def assistedFetcher_run(button):
    global task
    task = "AssistedFetcher"
    exit_program(None)   #closing the graphical interface to run the DirectFetcher

# assisted mode main dialog
def assistedFetcher_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Junos Space | Assisted Mode')) 
    help = urwid.Text([u'In the assisted mode the tool will retrieve the device list from Junos Space and proceed to connect to them in parallel in order to retrieve the chassis information.'])
    
    generalSettings = menu_button(u'Settings', assistedFetcher_generalSettings_dialog)
    verifyFileButton = menu_button(u'Verify Junos Space connectity', assistedFetcher_verify)
    runButton = menu_button(u'Run', assistedFetcher_run)
    cancelButton = menu_button(u'Cancel', exit_window)

    top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings,verifyFileButton, runButton,cancelButton]))
     

##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


# direct mode > run  | creates the DirectFetcher object and runs the appropiate console tool
def directFetcher_run(button):
    global task
    task = "DirectFetcher"
    exit_program(None)   #closing the graphical interface to run the DirectFetcher


# direct mode > general settings window
def directFetcher_generalSettings_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Direct Mode > General Settings')) 
    help = urwid.Text([u'Please fill in the default username / password / port for SSH.'])
    
    tb_username=urwid.Edit(('textbox', u"Username :\n"))
    tb_password=urwid.Edit(('textbox', u"Password :\n"),mask="*")
    tb_port=urwid.Edit(('textbox', u"Port :\n"))
    tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))
    cancelButton = menu_button(u'Cancel', exit_window)

    ### loading previouse settings
    def load_settings():
        try:
            settings=None
            with open('directFetcher.conf') as data_file:    
               settings = json.load(data_file)
            tb_username.set_edit_text(settings["username"])
            tb_password.set_edit_text(settings["password"])
            ### loading the ports list from the json array format needs flattening
            str_port=""
            for port in settings["port"]:
                str_port+=port+","
            str_port=str_port.strip(",")
            tb_port.set_edit_text(str_port)
            tb_parallelProcesses.set_edit_text(settings["parallelProcesses"])

        except:
            messageBox("Error", "An error occured while attempting to load existing settings!")

  
    def saveButton_onclick(button):
        ### validation of the fields        
        username=tb_username.get_edit_text()
        password=tb_password.get_edit_text()
        port=tb_port.get_edit_text()
        parallelProcesses=tb_parallelProcesses.get_edit_text()
        
        if len(str(username)) < 3:
            messageBox("Input Error", "Username needs to have at least 3 charcters!")
            return
        if len(str(password)) < 3:
            messageBox("Input Error", "Password needs to have at least 3 charcters!")
            return
        if len(str(port)) == 0:
            messageBox("Input Error", "Port list cannot be left empty!")
            return
        if len(str(parallelProcesses)) == 0:
            messageBox("Input Error", "The number of parallel processes cannot be left empty!")
            return

        ports = port.split(",")
        for p in ports:
            if not validatePort(p):
                messageBox("Input Error", "The given port list is not valid!\nExpected syntax is port_1, port_2, ... where 0 < port_n < 65534 ")
                return
        if not validateParalellProcessNumber(parallelProcesses):
            messageBox("Input Error", "The given number of parallel processes is not valid!\nExpected values are between 0 - 25. ")
            return

        #### saving the settings to disk
        try:
            data={}
            data["username"]=username
            data["password"]=password
            data["port"]=ports
            data["parallelProcesses"]=parallelProcesses
            with open("directFetcher.conf", 'w') as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))

            messageBox("General Settings", "Settings have been saved succesfull!")
        except:
            messageBox("General Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                
    saveButton = menu_button(u'Save', saveButton_onclick)

    top.open_box(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_username,tb_password, tb_port,tb_parallelProcesses,urwid.Divider(),saveButton,cancelButton]))
    load_settings()


       
     
# direct mode main dialog
def directFetcher_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Direct Mode')) 
    help = urwid.Text([u'In the direct mode the tool will retrieve the device list from \'hosts.csv\' file, will proceed to connect on all devices in a parallel fashion and retrieve the requested chassis information.'])
    
    generalSettings = menu_button(u'Settings', directFetcher_generalSettings_dialog)
    verifyFileButton = menu_button(u'Verify \'hosts.csv\' ', directFetcher_verify)
    runButton = menu_button(u'Run', directFetcher_run)
    cancelButton = menu_button(u'Cancel', exit_window)
    top.open_box(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings,verifyFileButton, runButton,cancelButton]))

    #top.open_box(urwid.Filler(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),generalSettings,verifyFileButton, runButton,cancelButton])))



# direct mode > verify  | creates a DirectFetcher object and attempts to load the inputs
def directFetcher_verify(button):
    captionLabel = urwid.Text(('standoutLabel',"Direct Mode > Verifying Inputs"))
    messageLabel = urwid.Text([""])
    button = menu_button(u'OK', exit_window)
   
    # creation of tool object
    df=DirectFetcher()
    (result,message)=df.LoadInputFile()
    messageLabel.set_text(message+"\n")
    dialog=top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))
  

def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')

def sub_menu(caption, choices):
    contents = menu(caption, choices)
    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u'...'], open_menu)

def menu(title, choices):
    body = [urwid.Text(('standoutLabel',title)), urwid.Divider()]
    body.extend(choices)
    body.extend([urwid.Divider(),urwid.Text([("","Copyright "),("standoutLabel","Juniper Networks"), (""," 2016 ")])])
    return urwid.Pile(urwid.SimpleFocusListWalker(body))
    
def item_chosen(button):
    response = urwid.Text([u'You chose ', button.label, u'\n'])
    done = menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))

def item_chosen(button):

    ask=urwid.Edit(('I say', u"What is your name?\n"))
    response = urwid.Text([u'You chose ', button.label, u'\n'])

    def on_ask_change(edit, new_edit_text):
        response.set_text(('I say', u"Nice to meet you, %s" % new_edit_text))
    urwid.connect_signal(ask, 'change', on_ask_change)
    
    done = menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response,ask, done])))


    
def exit_window(button):
    top.keypress(0,'esc')

def exit_program(button):
    raise urwid.ExitMainLoop()

menu_top = menu(u'Chassis Information Fetcher', [
    urwid.Divider(),
    menu_button(u'Direct Fetcher', directFetcher_dialog),
    menu_button(u'Junos Space | Assisted Fetcher', assistedFetcher_dialog),
    menu_button(u'Junos Space | Service Now Service Inside Fetcher', directFetcher_dialog),
    menu_button(u'Junos Space | Full Fetcher', fullFetcher_dialog),
    urwid.Divider(),
    menu_button(u'Help', directFetcher_dialog),
    menu_button(u'About', directFetcher_dialog),
    urwid.Divider(),
    menu_button(u'Exit', exit_program),
 
])

class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'/'))
        self.box_level = 0
        self.open_box(box)

    def message_box(self, box):
        box=urwid.Filler(box,valign='top')
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 90),
            valign='middle', height=('relative', 30),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1
        return self.original_widget

    def open_box(self, box):
        
        fbox=urwid.Filler(box,valign='top')
        self.original_widget = urwid.Overlay(urwid.LineBox(fbox),
            self.original_widget,
            align='center', width=('relative', 90),
            valign='middle', height=('relative', 90),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1
        return self.original_widget

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(CascadingBoxes, self).keypress(size, key)

top = CascadingBoxes(menu_top)

palette = [
            ('textbox', 'default,bold', 'default', 'bold'),
            ('standoutLabel', 'default,bold', 'default', 'bold'),
            
            ('reversed', 'standout', '')
          ]

urwid.MainLoop(top, palette=palette).run()

if task=="DirectFetcher":
    df=DirectFetcher()
    print("\n-------------------------------------------------")
    print("\n"+df.LoadInputFile()[1])
    print("\n-------------------------------------------------")
    print("\n"+str(df.Run()[1]))
    print("\n-------------------------------------------------")

if task=="AssistedFetcher":
    df=AssistedFetcher()
    print("\n-------------------------------------------------")
    print("\n"+df.LoadInputFile()[1])
    print("\n-------------------------------------------------")
    print("\n"+str(df.Run()[1]))
    print("\n-------------------------------------------------")



