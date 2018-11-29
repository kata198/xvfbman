#!/usr/bin/env python
#
# Copyright (c) 2018 Timothy Savannah under terms of LGPLv2.1
# You should have received a copy of this with this distribution as "LICENSE"
#


#vim: set ts=4 sw=4 expandtab

import os
import sys
from setuptools import setup


if __name__ == '__main__':
 

    dirName = os.path.dirname(__file__)
    if dirName and os.getcwd() != dirName:
        os.chdir(dirName)

    requires = []

    summary = 'A python module for managing Xvfb sessions / ensuring DISPLAY through a simple interface'

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Exception when reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='xvfbman',
            version='1.0.0',
            packages=['xvfbman'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            requires=requires,
            install_requires=requires,
            url='https://github.com/kata198/xvfbman',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv2',
            keywords=['python', 'Xvfb', 'manage', 'xvfbman', 'DISPLAY', 'X11', 'screen', 'Xorg', 'virtual', 'framebuffer'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Programming Language :: Python :: 3.5',
                          'Programming Language :: Python :: 3.6',
                          'Programming Language :: Python :: 3.7',
                          'Environment :: X11 Applications',
                          'Operating System :: POSIX',
                          'Topic :: Multimedia :: Graphics',
                          'Topic :: Software Development :: Libraries :: Python Modules',
                          'Topic :: Software Development :: Testing',
            ]
    )

#vim: set ts=4 sw=4 expandtab
