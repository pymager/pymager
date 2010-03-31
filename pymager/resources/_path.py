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

import os

class Path(object):
    def __init__(self, reference_directory, path_elements=[]):
        self.__reference_directory = reference_directory
        self.__path_elements = path_elements
    
    def parent_directory(self):
        return Path(self.__reference_directory, self.__path_elements[:-1])
    
    def absolute(self):
        return os.path.join(self.__reference_directory, *self.__path_elements)
    
    def relative(self):
        return os.path.join(*self.__path_elements)

    def append(self, path_element):
        return Path(self.__reference_directory, self.__path_elements + [path_element])
    
    def appendall(self, path_elements):
        return Path(self.__reference_directory, self.__path_elements + path_elements)
    
