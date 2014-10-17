#!/usr/bin/env python
#
# Copyright 2014 Yoann Gini
#
# LicenSetPermissionAndOwner under the Apache License, Version 2.0 (the "License");
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
import subprocess

from autopkglib import Processor, ProcessorError
from tempfile import NamedTemporaryFile

__all__ = ["SetPermissionAndOwner"]


class SetPermissionAndOwner(Processor):
    description = "Change permission and ownder for different paths."
    input_variables = {
        "chmod_list": {
            "required": False,
            "description": ("Pass an array of dictionary with followings keys: path, rights (value in chmod format), and recursive as bool (optional)."),
        },
        "chown_list": {
            "required": False,
            "description": ("Pass an array of dictionary with followings keys: path, owner (value in chown format), and recursive as bool (optional)."),
        },
    }
    output_variables = {
    }
    
    __doc__ = description
    
    def main(self):
        chmod_list = self.env.get('chmod_list', [])
        chown_list = self.env.get('chown_list', [])
        
        for path_info in chmod_list:
            path = path_info['path']
            rights = path_info['rights']
            recursive = False
            if path_info.has_key('recursive'):
                recursive = path_info['recursive']
            commands = []
            commands.append('sudo')
            commands.append('chmod')
            if recursive:
                commands.append('-R')
            commands.append(rights)
            commands.append(path)
            self.output("Set permission %s to %s" % (rights, path))
            command_result = subprocess.check_output(commands)
        
        for path_info in chown_list:
            path = path_info['path']
            owner = path_info['owner']
            recursive = False
            if path_info.has_key('recursive'):
                recursive = path_info['recursive']
            commands = []
            commands.append('sudo')
            commands.append('chown')
            if recursive:
                commands.append('-R')
            commands.append(owner)
            commands.append(path)
            self.output("Set owner %s to %s" % (owner, path))
            command_result = subprocess.check_output(commands)

if __name__ == '__main__':
    processor = SetPermissionAndOwner()
    processor.execute_shell()
    
