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
from datetime import datetime, timedelta
from imgserver import domain
from imgserver.domain.abstractitem import AbstractItem
from imgserver.domain.originalitem import OriginalItem
from imgserver.domain.deriveditem import DerivedItem
from tests.imgservertests import assertionutils

class OriginalItemTestCase(unittest.TestCase):
        
    def __checkItem(self, item):
        assert item.id == 'MYID12435'
        assert item.status == domain.STATUS_OK
        assert item.width == 800
        assert item.height == 600
        assert item.format == domain.IMAGE_FORMAT_JPEG
        assertionutils.check_last_status_date(item)
        
    def testShouldBeAbleToCreateItemWithWidthAndHeightAsString(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, ('800', '600'), domain.IMAGE_FORMAT_JPEG)
        self.__checkItem(item)
    
    def testShouldBeAbleToCreateItemWithWidthAndHeightAsInt(self):
        item = OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        self.__checkItem(item)
        
    def testShouldNotBeAbleToCreateItemWithNullId(self):
        try:
            OriginalItem(None, domain.STATUS_OK, (800, 600), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
            
    def testShouldNotBeAbleToCreateItemWithNullStatus(self):
        try:
            OriginalItem('MYID12435', None, (800, 600), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
            
    def testShouldNotBeAbleToCreateItemWithNullWidth(self):
        try:
            OriginalItem('MYID12435', domain.STATUS_OK, (None, 600), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
    
    def testShouldNotBeAbleToCreateItemWithNullHeight(self):
        try:
            OriginalItem('MYID12435', domain.STATUS_OK, (800, None), domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
        else:
            self.fail()
    
    def testShouldNotBeAbleToCreateItemWithNullFormat(self):
        try:
            OriginalItem('MYID12435', domain.STATUS_OK, (800, 600), None)
        except Exception:
            pass
        else:
            self.fail()
    
    def testSetStatusShouldUpdatelast_status_change_date(self):
        item = OriginalItem('MYID12435', domain.STATUS_INCONSISTENT, (800, 600), domain.IMAGE_FORMAT_JPEG)
        # fuck date by breaking encapsulation
        item._last_status_change_date = datetime.utcnow() - timedelta(1)
        item.status = domain.STATUS_OK
        assertionutils.check_last_status_date(item)