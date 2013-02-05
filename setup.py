import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='chipper',
    version="0.1",
    py_modules=['chipper'],
    provides=['chipper'],
    install_requires=['deconf'],
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/chipper",
    description="Refreshingly simple declarative logging that utilizes arbitrary tag sinks instead of traditional level handling",
    long_description=read('README.md'),
)
