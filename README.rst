========
Lab Test
========


.. image:: https://img.shields.io/pypi/v/labtest.svg
        :target: https://pypi.python.org/pypi/labtest

.. image:: https://img.shields.io/travis/CityOfBoston/labtest.svg
        :target: https://travis-ci.org/CityOfBoston/labtest

.. image:: https://readthedocs.org/projects/labtest/badge/?version=latest
        :target: https://labtest.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/coordt/labtest/shield.svg
     :target: https://pyup.io/repos/github/coordt/labtest/
     :alt: Updates

* Free software: BSD license
* Documentation: https://labtest.readthedocs.io.


Overview
--------

Easily create a semi-public, semi-independent deployment of a version of a web
site or app.

**Semi-public.** Allow access via a URL and user credentials. It would be available
from the public internet, but not to the general public.

**Semi-independent.** While the code will be independent, some of the other parts
of the infrastructure will be shared. The amount of sharing depends on needs.

**Version.** Typically this is a branch of development.

In short, it deploys branch `foo` onto a server that others can reach at `foo.test.example.com`.



Goals
-----

* Asynchronous evaluation of tickets
* Quick evaluation of new ideas
* Open evaluation to a greater audience



* To make the best test instances, you need:

    - A Machine User for your VCS (for private repos)
    - A Test server configuration in AWS
    - A `Dockerfile` that works
    - A script to build the container
    - A script to run commands in the container
    - Environment configuration capability
    - Access to a database backup, if necessary

``labtest create <branchname> [--name <name>]``

``labtest update <instancename>``

``labtest remove <instancename>``

``labtest stop [<instancename>]``

``labtest start [<instancename>]``

``labtest setsecret KEY=value``




Two phases: Bulid phase and install phase

    - Build phase
        - Git checkout of the repo
        - App build phase:
            - This phase does whatever is necessary to build the application before the docker container is built
            - Runs build commands in a specified docker container
            - The container maps a specified directory on the container to the git checkout
        - Container build phase
            - Builds using a specified Docker file and any other build params
            - Tags and uploads the image to repository
    - Install phase
        - setup service
        - setup environment vars
        - other parts of the docker stuff



- Specify a docker repo/image to use to build
- Code is checked out on main server, mapped to docker container
- Follow travis' or shippable's method for install and build

Features
--------

* TODO

Credits
---------

This package was created with Cookiecutter_ and the `lgiordani/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`lgiordani/cookiecutter-pypackage`: https://github.com/lgiordani/cookiecutter-pypackage

