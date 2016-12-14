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

from setuptools import setup, find_packages
import glob

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os

#py_files = glob.glob("../*.py")
#conf_files = glob.glob("../conf/*.conf")
#all_files=py_files+conf_files;
#packages = find_packages(where="../")
#print packages;


 

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        #os.system("git clone https://github.com/Juniper/py-space-platform.git")
        #os.system("sudo pip install ./py-space-platform")
        #os.system("rm -R py-space-platform")

        os.system("pip install urwid")
        os.system("pip install junos-eznc")
        os.system("echo \"cd /usr/local/lib/python2.7/dist-packages/ChassisInfoFetcher;python app.py\" > /usr/local/bin/ChassisInfoFetcher ; chmod +x /usr/local/bin/ChassisInfoFetcher")   
        os.system("cp bin/ChassisInfoFetcher-*.whl bin/ChassisInfoFetcher-latest-py2.py3-none-any.whl")

        install.run(self)


setup(
    name='ChassisInfoFetcher',
    version='1.0.1',
    url='https://git.juniper.net/asmeureanu/ChassisInfoFetcher',
    license='unknown',
    author='Alexandru Smeureanu',
    author_email='asmeureanu@juniper.net',
    description='ChassisInfoFetcher ',
    long_description=__doc__,
    #scripts = all_files,
    include_package_data = True,
    packages=["ChassisInfoFetcher","ChassisInfoFetcher.conf"],
    package_data={'ChassisInfoFetcher.conf':['*.conf']},
    zip_safe=False,

    platforms='any',
    install_requires=[
        'urwid'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',       
    ],

    cmdclass={
         'install': PostInstallCommand,
    },

)

