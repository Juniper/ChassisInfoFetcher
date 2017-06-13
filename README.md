# Tool description

The tool is designed to automatically connect to the customer devices, detect the device group type and fetch the necessary information for Advanced Services deliverables. The customer only needs to install the tool and run it in one of the following modes. 


Supported scenarios and modes are:
    
    Direct Mode -   In the direct mode the tool will retrieve the device list from 'hosts.csv' file, will proceed to connect 
                    to all devices in a parallel fashion and retrieve the information necessary for the Advanced Service deliverables.
    
    Junos Space | Assisted Mode - In the assisted mode the tool will retrieve the device list from Junos Space and proceed to connect to them 
                                  in parallel in order to retrieve the information necessary for the Advanced Service deliverables.
                                  
    Junos Space | SNSI Mode - In the SNSI mode the tool will retrieve the iJMB files collected by Junos Space from the devices and extract 
                                     the information necessary for the Advanced Service deliverables.
    
    Junos Space | Full Mode - In the full mode the tool will retrieve the device list from Junos Space and instruct Junos Space to connect to 
                                   all devices to retrieve the information necessary for the Advanced Service deliverables.


## 1. Installation using Docker

Note: For AS deliverables you need to populate the ChassisInfoFetcher/hosts.csv file with device information prior to executing the commands.

##### Building the Docker image
>docker build -t cif /sample/dir/with/file/ChassisInfoFetcher

##### Running the application inside a container
>docker run -it -v /sample/dir/with/file/ChassisInfoFetcher cif

##### After the ChassisInfoFetcher has finished execution
>docker ps -a 
Copy the Container ID corresponding to the IMAGE name "cif"

> cp Container-ID:/ChassisInfoFetcher/output/ /random/dir/of/your/choice

The output folder contains the necessary information. 

## 2. Installation without Docker

### 2.1 Basic dependencies 

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

#### Windows

>Not supported


### 2.2 Install the ChassisInfoFetcher tool
  
  To install PyEz : 
> pip install junos-eznc
  
  To install urwid :
> pip install urwid
  
  To install Space Ez :    
> git clone https://github.com/Juniper/py-space-platform.git

> sudo pip install ./py-space-platform

  To install the aplication
 > git clone https://git.juniper.net/mgospodinov/ChassisInfoFetcher.git 
    

## 3. How to run the tool via GUI?

To run the tool GUI :
   > python app.py
   
## 4. How to use the tool without GUI?

Individual scenarions can also be run separate:
   
   > python directFetcher.py "path"
   
   > python assistedFetcher.py "path"
   
   > python fullFetcher.py "path"
   
   > python SNSIFetcher.py "path"
   
Where the "path" attribute should be either "IB" if the information about the install base of the customer is needed, or "AS" to fetch all the necessary information for the Advanced Service deliverables. 
"IB" = Install Base
"AS" = Advanced Service deliverables  
   
### 4.1
The ChassisInfoFetcher (CIF) tool can be run without a GUI by executing the following commands directly. In order to successfully execute each mode, the login details required need to be included in the corresponding configuration files in the conf directory. Each fetcher has a specific login details that need to be provided.

   > python directFetcher.py "path"
   
In direct mode the tool retrieves the device list and login details stored in the ‘hosts.csv’ file and proceeds to connect to the devices in a parallel fashion. The hosts file can be found in the ChassisInfoFetcher2.0 directory. The format of each entry in the "hosts" file should be: 
<Device IP address, Username, Password, SSH port>
Alternatively, you can include only the IP address of the devices in the hosts file and specify the username, password, and SSH port in the Direct mode > Settings menu:

### Login details:
The conf/directFetcher.conf file needs to be configured with the following template:
{
    "parallelProcesses": "12",
    "password": "Device password",
    "port": [
        "22"
    ],
    "username": "Device login"
}
   > python assistedFetcher.py "path"

Format for the configuration of conf/assistedFetcher.conf:

{
    "device_ssh_password": "Device password",
    "device_ssh_username": "Device login",
    "js_password": "Junos Space password",
    "js_username": "Junos Space username",
    "parallelProcesses": "12",
    "port": [
        "list of ssh ports"
    ],
    "url": "Junos Space GUI IP address"
}

   > python fullFetcher.py "path"

Format of the configuration of conf/fullFetcher.py:
{
    "parallelProcesses": "12",
    "password_js": "Junos Space password",
    "url": "Junos Space GUI IP address",
    "username_js": "Junos Space username"
}


   > python SNSIFetcher.py "path"

The format of the configuration in conf SNSIFetcher.py is identical to that of conf/fullFetcher.py.

### 4.2 
Each mode is configured with a default set of commands that can be modified from the (* Mode > Commands menu). The commands are different based on the type of the device (MX, EX, SRX, etc.) and they can be modified from the corresponding device group menu. Note that only "show" commands and the "request support information" command can be executed by the tool - all others are not permitted. 

By default the necessary commands are provided in the commands directory of the tool. They are separated by device group: MX is used for the MX/vMX/M/T/ACX/PTX devices, QFX for the QFX/EX devices, and SRX for the SRX/vSRX devices. The numbers following the device type refer to the specific modes: MX_12 is for Direct and Assisted modes, MX_3 is for the SNSI mode and MX_4 is for the Full mode. The SNSI mode does not accept commands, because it uses the iJMB file to fetch the device configuration. 

Here you can find a mapping between the iJMB attachment files and the configuration information included in them:

        _AISESI.txt — Contains event support information; output of multiple Junos OS show commands 
        
        _rsi.txt — Contains “request support information” of the device 
        
        _cfg_xml.xml — Contains device configuration information in XML format (show configuration | display inheritance | display xml)
        
        _shd_xml.xml — Contains output of the “show chassis hardware” command in XML format 
        
        _ver_xml.xml — Contains the hostname and version information about the software (including the software help files and AI-Scripts bundle) running on the device (show version) 

This is why in the SNSI mode > Commands section, the relevant files are specified and not actual commands (for example, the section includes: _AISESI.txt, _cfg_xml, _shd_xml). Similarly the MX_3, QFX_3, and SRX_3 files do not contain commands.


## 5. Output

The configuration output from the devices is presented in two formats. 

Let us suppose that "show chassis hardware" and "show configuration | display inheritance" are run on RouterA and RouterB. Then two output files will be: router_RouterA (containing "show chassis hardware" and "show configuration | display inheritance" for RouterA), router_RouterB (containing "show chassis hardware" and "show configuration | display inheritance" for RouterB), show_chassis_hardware (containing "show chassis hardware" for RouterA and RouterB), and show_configuration_display_inheritance (containing "show configuration | display inheritance" for RouterA and RouterB).

The output of all commands in the SNSI and Full modes is in xml format with the exception of: "show configuration | display inheritance | display set" which is automatically parsed into a "set plain text" format by the tool. 


## 6. Use of Junos Space

Only Direct Mode does not require for Junos Space to be connected to the devices. All other modes use features from Junos Space, so for successful execution of the sctipt, make sure that your Junos Space is correctly connected to the respective devices.




    
    
    
