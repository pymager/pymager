from imgserver import domain

def original_yemmagouraya_metadata():
    return domain.OriginalImageMetadata('yemmaGouraya', domain.STATUS_OK, ('800', '600'), domain.IMAGE_FORMAT_JPEG)

def derived_100x100_yemmagouraya_metadata():
    return domain.DerivedImageMetadata(domain.STATUS_OK, ('100', '100'), domain.IMAGE_FORMAT_JPEG, original_yemmagouraya_metadata())