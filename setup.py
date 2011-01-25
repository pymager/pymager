#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name="pymager",
    version="0.5",
    author='Sami Dalouche',
    author_email='sami.dalouche@gmail.com',
    license='Apache-2.0',
    url='http://opensource.sirika.com/pymager',
    description='image conversion and rescaling RESTful web service',
    long_description="pymager is an image processing web service." 
        "Once images are uploaded using a RESTful web API,  "
        "it is possible to request any derivative of the image based on "
        "a different size or image format.",
    packages=find_packages(exclude=('tests', 'tests.*')),
#    scripts=['pymager-standalone.py'],
    include_package_data=True,
#    data_files=[('etc', ['etc/pymager-cherrypy.conf', 'etc/pymager.conf'])],
    test_suite="nose.collector",
    tests_require=['nose >= 0.11.1', 'mox >= 0.5.0'],
    install_requires=['PIL >= 1.1.6', 'SQLAlchemy >= 0.6.3', 'CherryPy >= 3.1.2', 'zope.interface >= 3.5.2'],
)
