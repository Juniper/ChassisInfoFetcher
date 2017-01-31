# coding: utf-8
#!/usr/bin/env python
"""
 ******************************************************************************
 * Copyright (c) 2016  Juniper Networks. All Rights Reserved.
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


class ui_help(ui_dialog):
    # assisted mode main dialog
    def ShowDialog(self,button):
        caption = urwid.Text(('standoutLabel',u'Help | Chassis Information Fetcher 2.0')) 
        help = urwid.Text([u"""The application is designed to help juniper equipments owners to retrive information about their devices for Advanced Services deliverables. It automatially detects the type of device (for example: MX, SRX, QFX) and executes the necessary "show" commands for that device.

It supports multiple operation modes:
     a) Direct mode
        In direct mode the tool retrieves the device list and login details stored in the ‘hosts.csv’ file and proceeds to connect to the devices in a parallel fashion. 
        The hosts file can be found in the ChassisInfoFetcher2.0 directory. The format of each entry in the file should be: 
        <Device IP address, Username, Password, SSH port>

        Alternatively, you can include only the IP address of the devices in the hosts file and specify the username, password, and SSH port in the Settings menu (Direct Mode > Settings).
 
        The Direct Mode > Commands section lists the commands that are to be executed by the tool for each device group – these can be modified by the engineer (note: only ‘show’ commands and ‘request support information’ are valid commands).

     b) Assisted mode
        In assisted mode the tool retrieves the device list from Junos Space. The Junos space login details as well as the login details of the devices need to be specified in the Settings section of Junos Space | Assisted Fetcher. 
        Afterwards the tool connects to all devices in parallel and extracts their chassis information.

     c) Service Inside Service Now (SNSI) mode
        In SNSI mode the tool connects to Junos Space, retrieves the iJMB files collected by Junos Space and extracts the needed chassis information. The Settings menu is the same as that of the Full Fetcher. 
        The following list provides the list of files that contain the configuration information. 

            •   *_AISESI.txt—Contains event support information; output of multiple Junos OS show commands
            •   *_rsi.txt—Contains “request support information” of the device
            •   *_cfg_xml.xml—Contains device configuration information in XML format (show configuration | display inheritance | display xml)
            •   *_shd_xml.xml—Contains output of the “show chassis hardware” command in XML format
            •   *_ver_xml.xml—Contains the hostname and version information about the software (including the software help files and AI-Scripts bundle) running on the device (show version)

        That is why in the command section of the Service Now Service Insight mode, the relevant files are specified and not actual commands (for example, include: _AISESI.txt, _cfg_xml, _shd_xml).

     d) Full mode
        In full mode the CIF tool retrieves the device list from Junos Space and instructs Junos Space to connect to all the devices in parallel. In this mode you need to enter only the Junos Space login details in the Settings menu.

            """])
        
        closeButton = self.menu_button(u'Close', self.exit_window)

        self.top.open_box(urwid.Pile([caption,help,closeButton]))
          
             
   