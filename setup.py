from setuptools import setup, find_packages
setup(
    name = "imgserver",
    version = "0.1",
    author = 'Sami Dalouche',
    author_email = 'sami.dalouche@gmail.com',
    license = 'LGPLv3',
    url= 'http://opensource.sirika.com/imgserver',
    packages = find_packages(exclude=('test','test.*')),
    scripts = ['imgserver.py'],
    include_package_data = True
    #package_data={'test.samples': ['*.jpg']}
)
#data_files=[('samples', ['tests/samples/brokenImage.jpg', 'tests/samples/sami.jpg'])]