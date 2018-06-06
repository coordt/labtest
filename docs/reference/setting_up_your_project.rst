=======================
Setting up your project
=======================

At this point, you may want to read the section on :ref:`how experiments work<admin/how_it_works:experiments>` to understand the process in more depth. Ultimately LabTest needs a Docker image and a configuration to launch experiments.

Twelve factors
==============

LabTest works best when your project adheres to the `12-factor app`_ methodology. A few factors are more important for working with LabTest: codebase; config; backing services; build, release, run; and disposability.

.. _12-factor app: https://12factor.net/


Codebase in version control
---------------------------

While use of version control is almost ubiquitous, it still is required as LabTest checks out the latest version of a branch instead of having a client upload data from a developer's computer.

The primary reason for this is to ensure reproducibility. If the developer forgets to check files into version control, and these non-version-controlled files are uploaded to an experiment, another developer will not be able to reproduce this experiment or update it properly.

`For more information see the 12-factor codebase page.`_

.. _for more information see the 12-factor codebase page.: https://12factor.net/codebase


Configuration via environment variables
---------------------------------------

Environment variables, passed into the Docker container, allow LabTest to dynamically configure your project. LabTest even has a :doc:`way to encrypt secrets</admin/secrets>` that are decrypted at runtime into environment variables.

`For more information see the 12-factor config page.`_

.. _for more information see the 12-factor config page.: https://12factor.net/config


Backing services
----------------

According to the `12-factor app definition`: A backing service is any service the app consumes over the network as part of its normal operation. LabTest allows you to specify what backing services you need in the experiment configuration. These backing services are provisioned and their configuration is passed via environment variables.

.. _12-factor app definition: https://12factor.net/backing-services


Build, release, run
-------------------

You can build your project anywhere, :doc:`including on LabTest's Laboratory,</reference/builtin_build_process>` as long as the final artifact is a Docker image. This image is combined with the experiment configuration as a Docker container (the release). Finally an OS service is set up to run it.

`For more information see the 12-factor Build, release, run page.`_

.. _for more information see the 12-factor build, release, run page.: https://12factor.net/build-release-run


Disposable
----------

One of LabTest's :ref:`about:architecture principles` is *Easily Rebuildable.* Everything in the Laboratory should be disposable and easily rebuildable. The longer and more complex it is to create or update an experiment, the less people will want to do it.

`For more information see the 12-factor disposability page.`_

.. _for more information see the 12-factor disposability page.: https://12factor.net/disposability


Containerizing your project
===========================

Your project might not run within a Docker container in production. However, a Docker container provides a nice, isolated environment with little overhead for creating these temporary experiments.


This topic is too broad to go into here, but the :ref:`Tutorial<tutorials/containerizing:containerizing>` demonstrates a very simple conversion. You'll know you are ready when you can run something like:

.. code-block:: console

    $ docker build -t myapp .
    $ docker run --rm -ti myapp

That means your container builds and runs locally.


Automating the app build process
================================

LabTest doesn't really care how you generate a Docker image. That said, there is a built-in process that will build your app and Docker image on the laboratory server.


Configuring for LabTest
=======================
