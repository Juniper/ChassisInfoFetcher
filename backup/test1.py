import urwid



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

def messageBox(caption,message):
    captionLabel = urwid.Text(('standoutLabel',caption))
    messageLabel = urwid.Text([message])
    
    button = menu_button(u'OK', exit_window)

    top.message_box(urwid.Filler(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button])))
   

# direct mode > general settings window
def directFetcher_generalSettings_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Direct Mode > General Settings')) 
    help = urwid.Text([u'Please fill in the default username / password / port for SSH.'])
    
    tb_username=urwid.Edit(('textbox', u"Username :\n"))
    tb_password=urwid.Edit(('textbox', u"Password :\n"),mask="*")
    tb_port=urwid.Edit(('textbox', u"Port :\n"))
    tb_parallelProcesses=urwid.Edit(('textbox', u"Number of parallel processes to be used : \n"))


    cancelButton = menu_button(u'Cancel', exit_window)

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
            f = open("directFetcher.conf", 'w');
            f.write("username = "+username+"\n")
            f.write("password = "+password+"\n")
            f.write("port = "+str(ports)+"\n")
            f.write("threads = "+str(parallelProcesses)+"\n")

            f.close()
            messageBox("General Settings", "Settings have been saved succesfull!")
        except:
            messageBox("General Settings > Error", "There were errors while attempting to save the settings to disk.\nPlease check permissions rights and/or locks for file: directFetcher.conf")
                
    saveButton = menu_button(u'Save', saveButton_onclick)


    top.open_box(urwid.Filler(urwid.Pile([caption,urwid.Divider(),help,urwid.Divider(),tb_username,tb_password, tb_port,tb_parallelProcesses,urwid.Divider(),saveButton,cancelButton])))

        
# direct mode main dialog
def directFetcher_dialog(button):
    caption = urwid.Text(('standoutLabel',u'Direct Mode')) 
    help = urwid.Text([u'In the direct mode the tool will retrieve the device list from \'hosts.csv\' file and proceed to connect on all of them in parallel to retrieve the chassis information.'])
    
    ask=urwid.Edit(('I say', u"Number of parallel threads: \n"))
    response = urwid.Text([u'You chose ', button.label, u'\n'])

   
    def on_ask_change(edit, new_edit_text):
        response.set_text(('I say', u"Nice to meet you, %s" % new_edit_text))
    urwid.connect_signal(ask, 'change', on_ask_change)

    generalSettings = menu_button(u'General Settings', directFetcher_generalSettings_dialog)
    verifyFileButton = menu_button(u'Verify \'hosts.csv\' ', exit_program)
    runButton = menu_button(u'Run', exit_program)
    cancelButton = menu_button(u'Cancel', exit_window)


    top.open_box(urwid.Filler(urwid.Pile([caption,urwid.Divider(),help, urwid.Divider(),response,ask, urwid.Divider(),generalSettings,verifyFileButton, runButton,cancelButton])))
  

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
    body.extend([urwid.Divider(),urwid.Text("Copyright Juniper Networks")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

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
    menu_button(u'Junos Space | Assisted Fetcher', directFetcher_dialog),
    menu_button(u'Junos Space | Service Now Service Inside Fetcher', directFetcher_dialog),
    menu_button(u'Junos Space | Full Fetcher', directFetcher_dialog),
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
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='left', width=('relative', 90),
            valign='top', height=('relative', 30),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
            self.original_widget,
            align='left', width=('relative', 90),
            valign='top', height=('relative', 90),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

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
