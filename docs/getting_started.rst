===============
Getting Started
===============

Getting your code ready
=======================

Containerize it
---------------

If your app doesn't already have a ``Dockerfile`` and a way to build everything as a container, you need to adapt it.

This topic is too broad to go into here. You'll know you are ready when you can run something like::

    docker build -t myapp .
    docker run --rm -ti myapp

That means your container builds and runs locally.

Automating the app build process
--------------------------------

Most web apps today require some compilation and building in order to be ready to deploy.

To do this, you need a build environment and a build command.

For the build environment, we need a Docker image that has all the tools you need pre-installed. This will be the :ref:`app_build_image_config_option` setting. We suggest choosing one of Shippable's `publicly available images`_ that fits your environment.

.. table::

   ========  =================
   Language  Recommended Image
   ========  =================
   Node.js   ``drydock/u16nodall``
   Clojure   ``drydock/u16cloall``
   Go        ``drydock/u16golall``
   PHP       ``drydock/u16phpall``
   Java      ``drydock/u16javall``
   Ruby      ``drydock/u16ruball``
   Python    ``drydock/u16pytall``
   Scala     ``drydock/u16scaall``
   C/C++     ``drydock/u16cppall``
   ========  =================

As you get more experienced, you can create your own custom environments.

.. _publicly available images: http://docs.shippable.com/platform/runtime/machine-image/ami-overview/


Set up Lab Test
===============

1. Install Lab Test locally
2. Configure Lab Test
    3. Create a ``.labtest.yml`` file in the root of your code repository if you don't already have a ``package.json`` file or a ``setup.cfg`` file.
    4. Add the following options:
        5. ``host``: set to your test server (see :ref:`host_config_option`)
        6. ``app_name``: set to the name of your app (see :ref:`app_name_config_option`)
        7. ``test_domain``: set to the test domain (see :ref:`test_domain_config_option`)
        8. ``code_repo_url``: set to the URL of the repository of your code (see :ref:`code_repo_url_config_option`)
9.
