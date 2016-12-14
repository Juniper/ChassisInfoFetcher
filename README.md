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

##Basic Dependencies

####Ubuntu 14.04

>apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev

####Ubuntu 16.04
 
>apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev

####CentOS 7

>yum install python-devel
>yum install python-lxml
>yum install openssl-devel

####MAC OS X El Capitan

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
 > git clone https://git.juniper.net/asmeureanu/ChassisInfoFetcher.git 
    

## How to run the tool via GUI?

To run the tool GUI :
   > python app.py
   
## How to use the tool without GUI?

Individual scenarions can also be run separate:
   
   > python directFetcher.py
   
   > python assistedFetcher.py
   
   > python fullFetcher.py
   
   > python SNSIFetcher.py
   
Settings file for the individual CLI tools are being stored in the conf/ folder

    
    
    
