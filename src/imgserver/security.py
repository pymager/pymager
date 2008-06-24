class SecurityCheckException(Exception):
    """Thrown when security requirements are not met while processing images """
    def __init__(self, message):
        Exception.__init__(self, message)

def imageTransformationSecurityDecorator(authorized_sizes):
    def decorator(func):
        def wrapper(transformation_request):
            if not transformation_request.size in authorized_sizes:
                raise SecurityCheckException, 'Requested size is not allowed'
            return func(transformation_request)
        return wrapper
    return decorator