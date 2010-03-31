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

class SecurityCheckException(Exception):
    """Thrown when security requirements are not met while processing images """
    def __init__(self, message):
        Exception.__init__(self, message)

def image_transformation_security_decorator(authorized_sizes):
    """ Throws an exception if the decorated method receives a 
    tranformation request with a wrong size"""
    def decorator(func):
        def wrapper(transformation_request):
            if authorized_sizes is not None and not transformation_request.size in authorized_sizes:
                raise SecurityCheckException('Requested size is not allowed')
            return func(transformation_request)
        return wrapper
    return decorator
