#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements/prod.txt') as req_file:
    requirements = [x for x in req_file.readlines() if x and x[0] not in ('-', '#')]

with open('requirements/test.txt') as req_file:
    test_requirements = [x for x in req_file.readlines() if x and x[0] not in ('-', '#')]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='labtest',
    version='0.2.1',
    description="Build an isolated test lab for running software in containers.",
    long_description=readme + '\n\n' + history,
    author="Corey Oordt",
    author_email='coreyoordt@gmail.com',
    url='https://github.com/coordt/labtest',
    packages=[
        'labtest',
    ],
    package_dir={'labtest':
                 'labtest'},
    entry_points={
        'console_scripts': [
            'labtest=labtest.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="BSD license",
    zip_safe=False,
    keywords='labtest',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
