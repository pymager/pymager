"""
    PyMager RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of PyMager.

    PyMager is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PyMager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with PyMager.  If not, see <http://www.gnu.org/licenses/>.

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
    