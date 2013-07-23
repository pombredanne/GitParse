from setuptools import setup, find_packages

setup(
    name='r6_commit',
    version='0.1.10',
    author='Shawn Crosby',
    author_email='scrosby@salesforce.com',
    packages=find_packages(),
    license='Be Real',
    url='https://pypi.python.org/pypi?r6_commit',
    description='Git Post Commit hook to parse log and create code review',
    long_description=open('README.txt').read(),
    install_requires=[
        "gus_client",
        "ccollab_client",
    ],
)
