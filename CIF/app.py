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




