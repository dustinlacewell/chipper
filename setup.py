from setuptools import setup

setup(
    name='chipper',
    version="0.1",
    py_modules=['chipper'],
    provides=['chipper'],
    requires=['deconf'],
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/chipper",
    description="Refreshingly simple declarative logging that utilizes arbitrary tag sinks instead of traditional level handling",
    long_description=open('README.md').read(),
)
