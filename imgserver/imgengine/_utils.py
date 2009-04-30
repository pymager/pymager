from imgserver.imgengine._illegalimageidexception import IllegalImageIdException
def checkid(image_id):
    if not image_id.isalnum():
        raise IllegalImageIdException(image_id)