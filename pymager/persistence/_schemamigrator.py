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
from zope.interface import Interface, implements

class SchemaMigrator(Interface):
    """ Manages the Schema, Metadata, and stores references to the Engine and Session Maker """
    
    def create_schema(self):
        """ Create  the database metadata """
            
    def drop_all_tables(self):
        """ Drop all tables """
        
    def session_template(self):
        """ Creates a Spring JDBC-like template """
         