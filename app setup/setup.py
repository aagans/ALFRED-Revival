"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['/Users/aale/Desktop/Projects/PopPolInterface/ALFRED Revival.py']
DATA_FILES = ['/Users/aale/Desktop/Projects/PopPolInterface/connected.png',
 '/Users/aale/Desktop/Projects/PopPolInterface/noconnect.png']
OPTIONS = {'iconfile': '/Users/aale/Desktop/Projects/PopPolInterface/phoenix.icns',
           'packages': 'mysql'}

setup(
    app=APP,
    version='1.0',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
