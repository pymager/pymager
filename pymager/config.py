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
import cherrypy
import os

GLOBAL_CONFIG_FILENAME = 'pymager-cherrypy.conf'
PYMAGER_CONFIG_FILENAME = 'pymager.conf'

_app_config = None

def app_config():
    return _app_config
    
class ConfigFileNotFoundError(Exception):
    def __init(self, directories):
        self.directories = directories
    def __str__(self):
        return self.directories.__str__()

def config_directories(caller_directory):
    """
    In order, we will look for config files in :
    # - ./ : useful when running pymager from /opt/pymager, 
        for instance : each instance has its own config file
    # - ./etc 
    # - caller_directory : Useful when running as WSGI, where the 
        config file is in the same directory as the WSGI script
    # - caller_directory/etc  
    # - /etc/pymager, /opt/local/etc/pymager
    
    @param caller_filename: pass __file__
    """
    config_directories = []
    
    # ./etc
    try:
        config_directories.append(os.path.join(os.getcwd(), 'etc'))
        config_directories.append(os.getcwd())
    except OSError, ose:
        if ose.errno != 2:
            raise
            # OSError: [Errno 2] No such file or directory. cwd doesn't exist
    
    # $SCRIPTDIR
    config_directories.append(caller_directory)
    config_directories.append(os.path.join(caller_directory, 'etc'))
    
    # /etc, /opt/local/etc, ..
    config_directories.extend(['/etc/pymager', '/opt/local/etc/pymager'])
    
    return config_directories

def parse_config(current_python_filename, filename):
    """
    @param current_python_filename: always pass __file__ !!! 
    """
    confdirs = config_directories(os.path.dirname(current_python_filename))
    for confdir in confdirs:
        try:
            parsed_config = cherrypy._cpconfig._Parser().dict_from_file(os.path.join(confdir, filename))
            _enforce_default_config(parsed_config)
            return parsed_config
        except IOError, e:
            pass
    raise ConfigFileNotFoundError(confdirs)

def _enforce_default_config(parsed_config):
    root_config = parsed_config['/'] if '/' in parsed_config else {}
    root_config['tools.trailing_slash.on'] = False
    root_config['request.dispatch'] = cherrypy.dispatch.MethodDispatcher()
    #root_config['request.process_request_body'] = False
    parsed_config['/'] = root_config
    
    
def set_app_config(app_config):
    global _app_config
    _app_config = app_config