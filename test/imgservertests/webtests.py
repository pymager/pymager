import exceptions
import unittest
from imgserver.web.derivedresource import DerivedItemUrlDecoder,UrlDecodingError

class DerivedItemUrlDecoderTestCase(unittest.TestCase):
        
    def testShouldBeAbleToDecodeUrlSegment(self):
        url_segment = 'item123-800x600.JPEG'
        decoded = DerivedItemUrlDecoder(url_segment)
        self.assertEqual('item123', decoded.itemid)
        self.assertEqual(800, decoded.width)
        self.assertEqual(600, decoded.height)
        self.assertEqual('JPEG', decoded.format)
    
    def testFormatShouldBeUppercased(self):
        url_segment = 'item123-800x600.jpeg'
        decoded = DerivedItemUrlDecoder(url_segment)
        self.assertEqual('JPEG', decoded.format)
    
    def testBadUrlSegmentShouldThrowException(self):
        try:
            decoded = DerivedItemUrlDecoder('item123800x600.jpg')
            self.fail()
        except UrlDecodingError:
            pass

def suite():
    return unittest.TestSuite(unittest.makeSuite(DerivedItemUrlDecoderTestCase, 'test'))