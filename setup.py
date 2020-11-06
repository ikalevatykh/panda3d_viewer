"""A setuptools based setup module."""

from setuptools import setup, find_packages
from os import path
from io import open  # for python 2.7


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='panda3d_viewer',
    version='0.3.1-dev',
    description='Easy-to-use python 3D graphics viewer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ikalevatykh/panda3d_viewer',
    author='Igor Kalevatykh',
    author_email='kalevatykhia@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
    ],
    keywords='rendering graphics 3d visualization',
    packages=find_packages(),
    install_requires=['numpy', 'panda3d>=1.10'],
)
