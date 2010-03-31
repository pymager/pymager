"""
   Copyright 2010 Sami Dalouche

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from pymager import config
import unittest

class ConfigTestCase(unittest.TestCase):
    
    def test_should_contain_six_elements(self):
        dirs = config.config_directories('bla')
        assert dirs is not None
        self.assertEquals(6, len(dirs))
        # not sure what to test besides copy/pasting the logic of the function itself..
        
        
