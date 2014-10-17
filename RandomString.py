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
import random
import string

from autopkglib import Processor, ProcessorError

__all__ = ["RandomString"]


class RandomString(Processor):
    description = ("Generate a random printable string (without spaces and return).")
    input_variables = {
        "random_string_length": {
            "required": False,
            "description": ("The string length, 42 by default."),
        },
    }
    output_variables = {
        "random_string": {
            "description": ("The random string."),
        },
    }
    
    __doc__ = description
    
        
    def main(self):
        random_string_length = self.env.get('random_string_length', 42)
        self.env['random_string'] = ''.join(random.choice(string.printable.strip().strip(''''"''')) for i in range(random_string_length))

if __name__ == '__main__':
    processor = RandomString()
    processor.execute_shell()
    
