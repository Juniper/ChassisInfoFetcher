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

if task=="DirectFetcherIB":
    df=DirectFetcher("IB")
    print("\n--------------------------------------------------------------------")
    print("\n  Direct Mode")
    print("\n--------------------------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="DirectFetcherAS":
    df=DirectFetcher("AS")
    print("\n--------------------------------------------------------------------")
    print("\n  Direct Mode")
    print("\n--------------------------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="AssistedFetcherIB":
    df=AssistedFetcher("IB")
    print("\n--------------------------------------------------------------------")
    print("\n  Assisted Mode")
    print("\n--------------------------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="AssistedFetcherAS":
    df=AssistedFetcher("AS")
    print("\n--------------------------------------------------------------------")
    print("\n  Assisted Mode")
    print("\n--------------------------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="FullFetcherIB":
    df=FullFetcher("IB")
    print("\n-------------------------------------------------")
    print("\n  Full Mode ")
    print("\n-------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="FullFetcherAS":
    df=FullFetcher("AS")
    print("\n-------------------------------------------------")
    print("\n  Full Mode ")
    print("\n-------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="SNSIFetcherIB":
    df=SNSIFetcher("IB")
    print("\n-------------------------------------------------")
    print("\n  SNSI Mode ")
    print("\n-------------------------------------------------")
    df.LoadInputFile()
    df.Run()

elif task=="SNSIFetcherAS":
    df=SNSIFetcher("AS")
    print("\n-------------------------------------------------")
    print("\n  SNSI Mode ")
    print("\n-------------------------------------------------")
    df.LoadInputFile()
    df.Run()




