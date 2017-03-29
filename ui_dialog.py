
#!/usr/bin/env python
# <*******************
# 
# Copyright 2017 Juniper Networks, Inc. All rights reserved.
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
# Unless required by applicable law or otherwise agreed to in writing by the parties, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# 
# *******************>


import urwid
import json
from urlparse import urlparse

from directFetcher import DirectFetcher
from assistedFetcher import AssistedFetcher
from fullFetcher import FullFetcher
 
### class responsible for drawing the dialog frames / background in the correct alingment
class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self):
        pass

    def init(self, box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'/'))
        self.box_level = 0
        self.open_box(box)

    ### function that creates the overlay and line frame for message boxes calls
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

    ### function that creates an overlay and the line frame around it, it also deals with the positioning of this "dialog frame" based on hierachy
    def open_listbox(self, box):
        
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
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

    ### function that creates an overlay and the line frame around it, it also deals with the positioning of this "dialog frame" based on hierachy
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

    ### function that intercepts the key press esc to keep track of hierarcy position
    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(CascadingBoxes, self).keypress(size, key)


### base class inherited by all dialogs in the application
class ui_dialog:
    def __init__(self,top):
        self.top=top
        pass

    # abstract method must be implemented by derived class    
    def ShowDialog(self):
        raise NotImplementedError 

    # abstract method must be implemented by derived class    
    def Run(self):
        raise NotImplementedError
    
    ###
    ###     Basic building blocks / functions to manipulate a dialog within the application
    ###         These are inherited and used by all the dialogs definde in the aplication
    ###


    ### function that will close the top most window when called    
    def exit_window(self,button):
        self.top.keypress(0,'esc')

    ### function that will close the main application loop killing thus all the opened dialogs
    def exit_program(self,button):
        raise urwid.ExitMainLoop()

    ### function  that creates a simple dialog with one message used as MessageBox type informational dialog
    def messageBox(self,caption,message):
        captionLabel = urwid.Text(('standoutLabel',caption))
        messageLabel = urwid.Text([message])
        button = self.menu_button(u'OK', self.exit_window)
        self.top.message_box(urwid.Pile([captionLabel, urwid.Divider(),messageLabel,urwid.Divider(),button]))
    
    ### function that attaches the callback for the buttons part of menu and sub_menus   
    def menu_button(self,caption, callback):
        button = urwid.Button(caption)
        urwid.connect_signal(button, 'click', callback)
        return urwid.AttrMap(button, None, focus_map='reversed')

    ### function that draws the menu items for all sub dialogs in the application
    def sub_menu(self,caption, choices):
        contents = menu(caption, choices)
        def open_menu(button):
            return self.top.open_box(contents)
        return menu_button([caption, u'...'], open_menu)
    
    ### function that draws the menu items for the main application dialog
    def menu(self,title, choices):
        body = [urwid.Text(('standoutLabel',title)), urwid.Divider()]
        body.extend(choices)
        body.extend([urwid.Divider(),urwid.Text([("","Copyright "),("standoutLabel","Juniper Networks"), (""," 2016 ")])])
        return urwid.Pile(urwid.SimpleFocusListWalker(body))
        