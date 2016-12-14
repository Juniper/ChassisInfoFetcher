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
import os
from urlparse import urlparse

from directFetcher import DirectFetcher
from assistedFetcher import AssistedFetcher
from fullFetcher import FullFetcher
from SNSIFetcher import SNSIFetcher

from ui_main import ui_main 
import ui_dialog

import logging
import logging.config

 
if not os.path.exists("output"):
    os.makedirs("output")   #create a folder called output for storing the logs

top = ui_dialog.CascadingBoxes()   ### create the dialog drawing context
main=ui_main(top)                  ### initialize the main dialog of the application
top.init(main.ShowDialog())        ### ask the drawing context to display the main dialog
main.ShowDisclaimer()

palette = [
            ('textbox', 'default,bold', 'default', 'bold'),
            ('standoutLabel', 'default,bold', 'default', 'bold'),            
            ('reversed', 'standout', '')
          ]                       ### general pallet used across the application




### Kickstart the GUI
urwid.MainLoop(top, palette=palette).run()
logging.config.fileConfig('conf/logging.conf')  ### enabling logging

### If an option was selected in the GUI execute it

task=""
if os.path.exists("execute.task"):
    with open("execute.task") as f:
        task = f.read()
    os.remove("execute.task")

if task=="DirectFetcher":
    df=DirectFetcher()
    print("\n--------------------------------------------------------------------")
    print("\n  Direct Mode")
    print("\n--------------------------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="AssistedFetcher":
    df=AssistedFetcher()
    print("\n--------------------------------------------------------------------")
    print("\n  Assisted Mode")
    print("\n--------------------------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="FullFetcher":
    df=FullFetcher()
    print("\n-------------------------------------------------")
    print("\n  Full Mode ")
    print("\n-------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="SNSIFetcher":
    df=SNSIFetcher()
    print("\n-------------------------------------------------")
    print("\n  SNSI Mode ")
    print("\n-------------------------------------------------")
    df.LoadInputFile()
    df.Run()




