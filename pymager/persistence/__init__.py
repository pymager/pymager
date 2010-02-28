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

from pymager.persistence._schemamigrator import SchemaMigrator
from pymager.persistence._transactional import SessionTemplate
from pymager.persistence._transactional import transactional
from pymager.persistence._transactional import begin_scope
from pymager.persistence._transactional import end_scope
from pymager.persistence._transactional import rollback
from pymager.persistence import _transactional

def init(sessionmaker):
    _transactional.init(sessionmaker=sessionmaker)
