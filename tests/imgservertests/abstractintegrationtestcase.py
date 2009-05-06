"""
    ImgServer RESTful Image Conversion Service 
    Copyright (C) 2008 Sami Dalouche

    This file is part of ImgServer.

    ImgServer is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ImgServer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with ImgServer.  If not, see <http://www.gnu.org/licenses/>.

"""
import unittest
from imgserver import bootstrap
import sqlalchemy 
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY='/tmp/imgserver-test'
    SAURI = 'sqlite:///:memory:'
    #SAURI = 'postgres://imgserver:funala@localhost/imgserver'
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        sqlalchemy.orm.clear_mappers()
        
        config = bootstrap.ServiceConfiguration(
            data_directory=AbstractIntegrationTestCase.DATA_DIRECTORY, 
            dburi=AbstractIntegrationTestCase.SAURI, 
            allowed_sizes=[(100*i,100*i) for i in range(1,9)],
            dev_mode= True)
        
        self._image_server_factory = bootstrap.ImageServerFactory(config)
        self._image_server = self._image_server_factory.create_image_server()
        self._image_metadata_repository = self._image_server_factory.image_metadata_repository        
    
        (getattr(self, 'onSetUp') if hasattr(self, 'onSetUp') else (lambda: None))()  
        
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        (getattr(self, 'onTearDown') if hasattr(self, 'onTearDown') else (lambda: None))()
        self._image_server_factory = None
        self._image_server = None
        self._image_metadata_repository = None
        self._schema_migrator = None
        
        #self.imageServerFactory.getConnection().close()
    