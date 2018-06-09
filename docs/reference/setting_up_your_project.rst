=======================
Setting up your project
=======================

At this point, you may want to read the section on :ref:`how experiments work<reference/how_it_works:experiments>` to understand the process in more depth. Ultimately LabTest needs a Docker image and a configuration to launch experiments.

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

According to the `12-factor app definition`_: A backing service is any service the app consumes over the network as part of its normal operation. LabTest allows you to specify what backing services you need in the experiment configuration. These backing services are provisioned and their configuration is passed via environment variables.

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


This topic is too broad to go into here because different technology stacks have different recommendations. We do have a page of :doc:`Docker container tips</reference/container_tips>` and the :ref:`Tutorial<tutorials/containerizing:containerizing>` demonstrates a very simple conversion. You'll know you are ready when you can run something like:

.. code-block:: console

    $ docker build -t myapp .
    $ docker run --rm -ti myapp

That means your container builds and runs locally.


Automating the app build process
================================

LabTest doesn't really care how you generate a Docker image. That said, there is a :doc:`built-in process</reference/builtin_build_process>` that will build your app and Docker image on the laboratory server.

At the end of this process, you need a Docker image that is available to the Laboratory server.


Configuring for LabTest
=======================

The LabTest configuration is designed to require little effort, but allow lots of customization. The configuration lives in your repository, possibly in one of your existing configuration files.

Read the section on :doc:`/reference/configuration` for detailed information.

Where to put the configuration?
-------------------------------

LabTest looks for its configuration information in three places: ``.labtest.yml``\ , ``setup.cfg``\ , and ``package.json``\ . Depending on your setup, pick one.

You can also choose :ref:`reference/configuration:alternate configuration files`.

Required configuration
----------------------

The :ref:`configuration:host` and :ref:`configuration:test_domain` attributes are required because there is no way that LabTest can derive a good default from the project.

App name
--------

The "App Name" is LabTest's way to namespace experiments. It is a good idea to set the :ref:`configuration:app_name` attribute. LabTest will default to the name of the directory of the Git project. However, developers have the ability to alter this, which will lead to issues if different developers try to update the same experiment, but LabTest defaults to different app names.

Configuring Backing services
----------------------------

If your project requires backing services, such as a database, you need to add them to your configuration. You can :doc:`read all about backing services</reference/backing_services/index>`.
