import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-publishable',
    version='0.1.9',
    packages=find_packages(),
    include_package_data=True,
    license='Apache Software License',
    description='A simple Django app to add draft/publish capabilities to your models.',
    long_description=README,
    url='https://github.com/Ilyes-Hammadi/django-publishable',
    author='Ilyes Hammadi',
    author_email='hammadiilyesahmed@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
)