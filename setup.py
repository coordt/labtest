#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('requirements/prod.txt') as req_file:
    requirements = [x for x in req_file.readlines() if x and x[0] not in ('-', '#')]

with open('requirements/test.txt') as req_file:
    test_requirements = [x for x in req_file.readlines() if x and x[0] not in ('-', '#')]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()


test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='labtest',
    version='0.3.1',
    description="Build an isolated test lab for running software in containers.",
    long_description=readme + '\n\n' + history,
    author="Corey Oordt",
    author_email='coreyoordt@gmail.com',
    url='https://github.com/CityOfBoston/labtest',
    packages=find_packages(exclude=['tests*', 'docs', 'build', ]),
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
    python_requires='==2.7.*',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Environment :: Console',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
