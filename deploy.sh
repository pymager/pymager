#!/bin/sh

python setup.py sdist
rsync -avP dist/ samokk@sirika.com:/srv/http/developers.sirika.com/pymager-project/downloads/
