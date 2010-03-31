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
from datetime import datetime, timedelta
from pymager import domain
from tests.pymagertests import assertionutils

class OriginalImageMetadataTestCase(unittest.TestCase):
    
    def test_should_create_item_using_width_and_height_expressed_as_string(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, ('800', '600'), domain.IMAGE_FORMAT_JPEG)
        _item_should_match(item)
    
    def test_should_create_item_using_width_and_height_expressed_as_int(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        _item_should_match(item)
        
    def test_id_should_be_mandatory_at_creation_time(self):
        try:
            domain.OriginalImageMetadata(None, domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
            
    def test_status_should_be_mandatory_at_creation_time(self):
        try:
            domain.OriginalImageMetadata('MYID12435', None, (800, 600), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
            
    def test_width_should_be_mandatory_at_creation_time(self):
        try:
            domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (None, 600), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
    
    def test_heiht_should_be_mandatory_at_creation_time(self):
        try:
            domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, None), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
    
    def test_format_should_be_mandatory_at_creation_time(self):
        try:
            domain.OriginalImageMetadata('MYID12435', domain.STATUS_OK, (800, 600), None)
        except Exception:
            pass
        else:
            self.fail()
    
    def test_setting_status_should_update_status_change_date(self):
        item = domain.OriginalImageMetadata('MYID12435', domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
        # fuck date by breaking encapsulation
        item._last_status_change_date = datetime.utcnow() - timedelta(1)
        item.status = domain.STATUS_OK
        assertionutils.last_status_date_should_be_now(item)
        
def _item_should_match(item):
    assert item.id == 'MYID12435'
    assert item.status == domain.STATUS_OK
    assert item.width == 800
    assert item.height == 600
    assert item.format == domain.IMAGE_FORMAT_JPEG
    assertionutils.last_status_date_should_be_now(item)
