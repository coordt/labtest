=============
About LabTest
=============

LabTest allows you to easily create a semi-public, semi-independent deployment of a version of a web site or app.

**Semi-public.** Allow access via a URL and optional user credentials. It would be available from the public internet, but not necessarily to the general public.

**Semi-independent.** While the code will be independent, some of the other parts of the infrastructure can be shared. The amount of sharing depends on needs and budget.

**Version.** Typically this is a branch of development.

In short, LabTest deploys branch ``foo`` onto a server that others can reach at ``foo.test.example.com``\ . This deployment is called an *experiment.*

Put another way, it is a framework to provision temporary isolated infrastructures based on configurations that can be stored in a public code repositories.

What can you do with it?
========================

**Parallel development.** One developer can complete three tickets, in three different branches, and publish the three experiments for review by three different people. As the tickets are completed, the branches can be merged and the experiments deleted in any order.

**Quick evaluation of new ideas.** Sometimes you just want to try something. LabTest makes it easy to demonstrate the idea.

**Open evaluation to a greater audience.** When the experiments are accessible from the internet, people don't have to look over the developer's shoulder to see the progress.

**Provision one-time use apps.** At its core, LabTest provisions isolated temporary infrastructure. You could use this to make it easy to set up and tear down an app for a one-time use.


Functional Principles
=====================

As we develop LabTest, these are things we keep in mind on how LabTest should work for teams.

**Easy for developers to use.** There are several parts to this. It should be require as few steps as possible to:

- onboard a new developer
- create, update, and delete experiments
- convert a code base to use LabTest

**Easy to administrate.** LabTest only requires SSH access to the environment. Anything else you want to do is up to you.

**Flexible.** No two teams are alike. LabTest embraces this diversity by providing good defaults (for ease of use) with the ability to customize and extend (to make it your own).


Architecture Principles
=======================

**Isolated Environment.** Because this is a test environment, things will go wrong. You do not want an accident to harm another environment. This is also handy for security reasons. Since the developers will have SSH access to the test server, you want to limit the amount of damage a hacker could do if you are compromised.

**Easily Rebuildable.** If something goes wrong, make it easy to scrap everything and rebuild from scratch. While rebuilding the environment might be inconvenient, it is easier than debugging what changed in the developer playground.

**Flexible Laboratory Administration.** By default, LabTest is designed to require very little administration. LabTest does allow for flexible methods for administrators to define defaults and expand the capabilities. Laissez-faire or fascist: you can administrate your way.

**Accessible by developers via SSH.** The primary reason is that it is via SSH that the commands will communicate to set up each test instance. The other is that there are occasions when a developer having access to a production-like environment is advantageous. Being able to tweak things on the server is a quick and easy way to debug.


.. include:: ../AUTHORS.rst

Colophon
========

This package was initially created by Corey Oordt for the `City of Boston`_ using Cookiecutter_ and the `lgiordani/cookiecutter-pypackage`_ project template.

.. _city of boston: https://www.boston.gov/
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _lgiordani/cookiecutter-pypackage: https://github.com/lgiordani/cookiecutter-pypackage


