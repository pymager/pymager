#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "imgserver",
    version = "0.1",
    author = 'Sami Dalouche',
    author_email = 'sami.dalouche@gmail.com',
    license = 'LGPLv3',
    url= 'http://opensource.sirika.com/imgserver',
    packages = find_packages(exclude=('test','test.*')),
    scripts = ['imgserver-standalone.tac'],
    include_package_data = True,
    test_suite= "test"
    #install_requires="pil >= 1.1.6"
    #package_data={'test.samples': ['*.jpg']}
)
#data_files=[('samples', ['tests/samples/brokenImage.jpg', 'tests/samples/sami.jpg'])]
