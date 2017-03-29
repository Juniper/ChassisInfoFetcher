
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
import utils
from assistedFetcher import AssistedFetcher
from urlparse import urlparse
from ui_dialog import ui_dialog
import utils


class ui_about(ui_dialog):
    # assisted mode main dialog
    def ShowDialog(self,button):
        caption = urwid.Text(('standoutLabel',u'About | Chassis Information Fetcher')) 
        about = urwid.Text([u"""The application was developed in a joined effort by:

            Alexandru Smeureanu 
            Hans Rinsema
            Leo Edwards
            Michael Kim
            Mitko Gospodinov
            Mohcene Fares
            Stephen Steiner

            """])
        
        closeButton = self.menu_button(u'Close', self.exit_window)

        self.top.open_box(urwid.Pile([caption,urwid.Divider(),about, urwid.Divider(),closeButton]))
          
             
   