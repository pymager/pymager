from setuptools import setup, find_packages
setup(
    name = "imgserver",
    version = "0.1",
    author = 'Sami Dalouche',
    author_email = 'sami.dalouche@gmail.com',
    url= 'http://opensource.sirika.com/imgserver',
    packages = find_packages(exclude=('tests','tests.*')),
    scripts = ['imgserver.py'],
    package_data={'imgserver': ['tests/samples/*.jpg']}
)
#data_files=[('samples', ['tests/samples/brokenImage.jpg', 'tests/samples/sami.jpg'])]