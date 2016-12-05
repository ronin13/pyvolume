#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


with open('requirements_dev.txt') as f:
    test_requirements = f.read().splitlines()


setup(
    name='pyvolume',
    version='0.1.1',
    description="Python Docker Volume driver",
    long_description=readme + '\n\n' + history,
    author="Raghavendra Prabhu",
    author_email='me@rdprabhu.com',
    url='https://github.com/ronin13/pyvolume',
    packages=[
        'pyvolume',
    ],
    package_dir={'pyvolume':
                 'pyvolume'},
    entry_points={
        'console_scripts': [
            'pyvolume = pyvolume.manager:start'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyvolume',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
