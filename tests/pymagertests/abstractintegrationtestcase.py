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

import unittest
from pymager import bootstrap
from pymager import persistence
import sqlalchemy 
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY = '/tmp/pymager-test'
    SAURI = 'sqlite:///:memory:'
    #SAURI = 'postgres://pymager:funala@localhost/pymager'
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        sqlalchemy.orm.clear_mappers()
        
        config = bootstrap.ServiceConfiguration(
            data_directory=AbstractIntegrationTestCase.DATA_DIRECTORY,
            dburi=AbstractIntegrationTestCase.SAURI,
            allowed_sizes=[(100 * i, 100 * i) for i in range(1, 9)],
            dev_mode=True)
        
        self._image_server_factory = bootstrap.ImageServerFactory(config)
        self._image_server = self._image_server_factory.create_image_server()
        self._image_metadata_repository = self._image_server_factory.image_metadata_repository
        self._sessionmaker = self._image_server_factory.sessionmaker
        self._session = persistence.begin_scope(self._sessionmaker)    
    
        (getattr(self, 'onSetUp') if hasattr(self, 'onSetUp') else (lambda: None))()  
        
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        (getattr(self, 'onTearDown') if hasattr(self, 'onTearDown') else (lambda: None))()
        self._image_server_factory = None
        self._image_server = None
        self._image_metadata_repository = None
        self._schema_migrator = None
        persistence.end_scope(self._sessionmaker, force_rollback=True)
    
