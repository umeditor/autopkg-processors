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
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["AdaptRoundCubeConfiguration"]


class AdaptRoundCubeConfiguration(Processor):
    description = ("Custom processor to adapt RoundCube configuration to the current OS X Server config.")
    input_variables = {
        "roundcube_configuration_file": {
            "required": True,
            "description": ("The roundcube configuration file to adapt to current OS X Server."),
        },
    }
    
    output_variables = {}
    
    __doc__ = description
    
    def get_serveradmin_settings(self, settings):
        command_result = subprocess.check_output(['sudo', 'serveradmin', 'settings', settings]).split()[0]
        return command_result[len(settings)+4:-2]
        
    def main(self):
        roundcube_configuration_file = self.env['roundcube_configuration_file']
        config_file = open(roundcube_configuration_file, 'au')
        
        config_file.write('\n\n\n')
        config_file.write('### YGI AutoPkg Config\n')
        config_file.write('\n')
        
        mail_domain = self.get_serveradmin_settings('mail:postfix:mydomain')
        
        config_file.write('# Default domain name grabbed\n')
        config_file.write("$rcmail_config['mail_domain'] = '%s';\n" % mail_domain)
        
        config_file.write('# Authentication work only with CRAM-MD5\n')
        config_file.write("$rcmail_config['imap_auth_type'] = 'CRAM-MD5';\n")
        
        config_file.close()
        

if __name__ == '__main__':
    processor = AdaptRoundCubeConfiguration()
    processor.execute_shell()
    
