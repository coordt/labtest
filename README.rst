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

:Free software: BSD license
:Documentation: https://labtest.readthedocs.io.


Overview
--------

In short, LabTest deploys branch ``foo`` onto a server that others can reach at ``foo.test.example.com``\ . This deployment is called an *experiment.*

There are three parts to LabTest: the server architecture (or *laboratory),* the command line client, and the configuration in the code repository.

**The laboratory.** This is the server environment that you control. LabTest has some templates to help you get started, but ultimately the laboratory's environment is under your control. All LabTest needs is SSH access and Docker.

**The configuration.** The configuration instructs LabTest how to publish experiments. It sits in the code repository so any developer who works on the code can publish new experiments.

**The client.** The client is a command line tool that uses SSH and the configuration to create, list, update, and delete experiments in the laboratory.

Goals
-----

- Easy for developers to use
- Easy to administrate
- Flexible enough to conform to different team methodologies

**Easy for developers to use.** There are several parts to this. It should be require as few steps as possible to:

- onboard a new developer
- create, update, and delete experiments
- convert a code base to use LabTest

**Easy to administrate.** LabTest only requires SSH access to the environment. Anything else you want to do is up to you.

**Flexible.** No two teams are alike. LabTest embraces this diversity by providing good defaults (for ease of use) with the ability to customize and extend (to make it your own).

What can you do with it?
------------------------

**Asynchronous evaluation of tickets.** A developer can complete three tickets, in three different branches, and publish the three experiments for review by different people. As the tickets are completed, the branches can be merged and the experiments deleted in any order.

**Quick evaluation of new ideas.** Sometimes you just want to try something. LabTest makes it easy to demonstrate the idea.

**Open evaluation to a greater audience.** When the experiments are accessible from the internet, people don't have to look over the developer's shoulder to see the progress.


Credits
---------

This package was created with Cookiecutter_ and the `lgiordani/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`lgiordani/cookiecutter-pypackage`: https://github.com/lgiordani/cookiecutter-pypackage

