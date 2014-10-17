#!/usr/bin/env python
#
# Copyright 2014 Yoann Gini
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import platform
import plistlib

from distutils import version

from autopkglib import Processor, ProcessorError

__all__ = ["OSXServerOnly"]


class OSXServerOnly(Processor):
    description = ("Fail if the recipe isn't run on OS X Server. The process don't check if the server is actually configured")
    input_variables = {
        "minimum_system_version": {
            "required": True,
            "description": ("Execute sed commands against this file."),
        },
    }
    output_variables = {
        "os_x_system_version": {
            "description": ("The OS X version, can be 10.6.8, 10.7, 10.9.3, etc."),
        },
        "os_x_server_version": {
            "description": ("The Server.app version, can be 1, 3.1.2 or None if not a server or if Snow Leopard Server."),
        },
        "is_an_os_x_server": {
            "description": ("Is true is Server.app is here or if it's an OS X Snow Leopard Server"),
        },
        "is_a_modern_os_x_server": {
            "description": ("Is true is only if Server.app is here"),
        },
    }
    
    __doc__ = description
    
        
    def main(self):
        minimum_system_version = self.env.get('minimum_system_version', None)
        server_app_info_plist_path = "/Applications/Server.app/Contents/Info.plist"
        server_app_library_folder = "/Library/Server"
        snow_server_serveradmin_path = "/usr/sbin/serveradmin"
        
        is_an_os_x_server = False
        is_a_modern_os_x_server = False
        
        os_x_system_version = platform.mac_ver()[0]
        
        os_x_server_version = None
        if version.StrictVersion(os_x_system_version) >= version.StrictVersion('10.7') and os.path.exists(server_app_info_plist_path) and os.path.exists(server_app_library_folder):
            server_info = plistlib.readPlist(server_app_info_plist_path)
            os_x_server_version = server_info['CFBundleShortVersionString']
            is_an_os_x_server = True
            is_a_modern_os_x_server = True
        elif os.path.exists(snow_server_serveradmin_path):
            is_an_os_x_server = True
        
        if not is_an_os_x_server:
            raise ProcessorError("Current system isn't an OS X Server")
        
        if minimum_system_version:
            if version.StrictVersion(os_x_system_version)  < version.StrictVersion(minimum_system_version):
                raise ProcessorError("Minimum supported OS X version is %s" % minimum_system_version)
                
        self.env['os_x_system_version'] = os_x_system_version
        self.env['os_x_server_version'] = os_x_server_version
        self.env['is_an_os_x_server'] = is_an_os_x_server
        self.env['is_a_modern_os_x_server'] = is_a_modern_os_x_server

if __name__ == '__main__':
    processor = OSXServerOnly()
    processor.execute_shell()
    
