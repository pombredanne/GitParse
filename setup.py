from setuptools import setup, find_packages

setup(
    name='git_logparser',
    version='0.1.0',
    author='Shawn Crosby',
    author_email='scrosby@salesforce.com',
    packages=find_packages(),
    license='Be Real',
    url='https://pypi.python.org/pypi?r6_commit',
    description='Library to parse Git Logs',
    long_description=open('README.txt').read(),
)
