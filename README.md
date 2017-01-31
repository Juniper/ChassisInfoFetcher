# Tool description

Tool designed to help in retrival of chassis information from Juniper devices in situation in which Junos Space Service Now is not installed or not permitted to send data.


Supported scenarios and modes are:
    
    Direct Mode -   In the direct mode the tool will retrieve the device list from 'hosts.csv' file, will proceed to connect 
                    on all devices in a parallel fashion and retrieve the requested chassis information.
    
    Junos Space | Assisted Mode - In the assisted mode the tool will retrieve the device list from Junos Space and proceed to connect to them 
                                  in parallel in order to retrieve the chassis information.
    
    Junos Space | Full Mode - In the full mode the tool will retrieve the device list from Junos Space and instruct Junos Space to connect to 
                                   all devices to retrieve the chassis information.

    Junos Space | SNSI Mode - In the SNSI mode the tool will retrieve the iJMB files collected by Junos Space from the devices and extract 
                                     the needed chassis information.

## Installation using Docker

##### Downloading the Dockerfile build instructions
>wget https://git.juniper.net/mgospodinov/ChassisInfoFetcher2.0/raw/master/docker/Dockerfile

##### Building the Docker image
>docker build -t juniper/chassisinfofetcher .

##### Running the application inside a container
>docker run -i -t juniper/chassisinfofetcher  /bin/ash -c "cd ChassisInfoFetcher;/usr/bin/python2.7 app.py"

##### Start a container in shell for manual execution
>docker run -i -t juniper/chassisinfofetcher  /bin/ash 

## Basic Dependencies

#### Ubuntu 14.04

>apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev

#### Ubuntu 16.04
 
>apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev

#### CentOS 7

>yum install python-devel
>yum install python-lxml
>yum install openssl-devel

#### MAC OS X El Capitan

>Xcode
>easy_install pip

## To install the ChassisInfoFetcher tool
 
#### Dependencies:
  
  To install PyEz : 
> pip install junos-eznc
  
  To install urwid :
> pip install urwid
  
  To install Space Ez :    
> git clone https://github.com/Juniper/py-space-platform.git

> sudo pip install ./py-space-platform

  To install the aplication
 > git clone https://git.juniper.net/mgospodinov/ChassisInfoFetcher2.0.git 
    

## How to run the tool via GUI?

To run the tool GUI :
   > python app.py
   
## How to use the tool without GUI?

Individual scenarions can also be run separate:
   
   > python directFetcher.py
   
   > python assistedFetcher.py
   
   > python fullFetcher.py
   
   > python SNSIFetcher.py
   
The CIF tool can be run without a GUI by executing the following commands directly. In order to successfully execute each fetcher, the login details required need to be included in the corresponding files in the conf directory. Each fetcher has a separate command: 

    > python directFetcher.py

The conf/directFetcher.conf file needs to be configured with the following template:
{
    "parallelProcesses": "10",
    "password": "Device password",
    "port": [
        "22"
    ],
    "username": "Device username"
}
    > python assistedFetcher.py

Format for the configuration of conf/assistedFetcher.conf:

{
    "device_ssh_password": "",
    "device_ssh_username": "",
    "js_password": "Junos Space password",
    "js_username": "Junos Space username",
    "parallelProcesses": "12",
    "port": [
        "list of ssh ports"
    ],
    "url": "Junos Space GUI IP address"
}

    > python fullFetcher.py
Format of the configuration of conf/fullFetcher.py:
{
    "parallelProcesses": "",
    "password_js": "Junos Space password",
    "url": "Junos Space GUI IP address",
    "username_js": "Junos Space username"
}


    > python SNSIFetcher.py
The format of the configuration in conf SNSIFetcher.py is identical to that of conf/fullFetcher.py.

## Output!

The configuration output from the devices is presented in two formats. 

Let us suppose that "show chassis hardware" and "show configuration | display inheritance" are run on RouterA and RouterB. Then two output files will be: router_RouterA (containing "show chassis hardware" and "show configuration | display inheritance" for RouterA), router_RouterB (containing "show chassis hardware" and "show configuration | display inheritance" for RouterB), show_chassis_hardware (containing "show chassis hardware" for RouterA and RouterB), and show_configuration_display_inheritance (containing "show configuration | display inheritance" for RouterA and RouterB).

The output of all commands in the SNSI and Full modes is in xml format with the exception of: "show configuration | display inheritance | display set" which is parsed into a "set" format. 


## Commands!




## Modes!

Only Direct Mode does not require for Junos Space to be connected to the devices. All other modes use features from Junos Space, so for successful execution of the sctipt, make sure that your Junos Space is correctly connected to the respective devices.




    
    
    
