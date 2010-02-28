#!/usr/bin/env python
from migrate.versioning.shell import main

main(url='postgres://pymager:pymager@localhost/pymager', repository='pymager_db')
