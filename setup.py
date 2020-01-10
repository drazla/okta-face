#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'face_recognition_models>=0.3.0',
    'Click>=6.0',
    'dlib>=19.7',
    'numpy',
    'Pillow'
]

test_requirements = [
    'tox',
    'flake8==2.6.0'
]

setup(
    name='okta_face',
    version='1.0.0',
    description="Combines facial recognition and the Okta Sign-In Widget",
    long_description=readme + '\n\n' + history,
    author="Darren Fowler",
    author_email='darren.fowler@okta.com',
    url='https://github.com/drazla/okta_face',
    packages=[
        'okta_face',
    ],
    package_dir={'okta_face': 'okta_face'},
    package_data={
        'okta_face': ['models/*.dat']
    },
    install_requires=requirements,
    license="Apache-2.0",
    zip_safe=False,
    keywords='okta_face',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    python_requires='>2.7,'
)
