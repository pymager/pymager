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

class DeleteImagesCommand(object):
    """ Coordinates the deletion of an image metadata and files """
    
    def __init__(self, image_metadata_repository, session_template, path_generator, fetch_items_callback):
        """ Initializes a Delete Images Command with the following parameters
            @param image_metadata_repository: the repository for image metadata
            @param session_template: the db session template
            @param path_generator: a PathGenerator instance
            @param fetch_items_callback: some function that will return a list of image metadata
            
        """
        self.__image_metadata_repository = image_metadata_repository
        self.__path_generator = path_generator
        self.__session_template = session_template
        self.__fetch_items_callback = fetch_items_callback
        
    def __cleanup_in_session(self):
        items = self.__fetch_items_callback()
        for i in items:
            os.remove(i.associated_image_path(self.__path_generator).absolute())
            self.__image_metadata_repository.delete(i)
        
    def execute(self):
        def execute_in_session(session):
            self.__cleanup_in_session()
        self.__session_template.do_with_session(execute_in_session)
    
