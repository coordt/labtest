.. _builtin_build_process:

======================
Built-in build process
======================

This process is meant to provide an easy way to get started with LabTest. It requires some :ref:`initial setup<setting_up_the_builtin_build_process>` to allow for easy code checkouts.

Configuration
=============

To use the built-in build process, you must set several configuration parameters.

:ref:`build_provider_config_option` must be set to ``local``\ .

Set :ref:`code_repo_url_config_option` to the URL for your code repository.

We'll discuss :ref:`app_build_image_config_option` and :ref:`app_build_command_config_option` in the next sections.

There is one optional parameter: :ref:`container_build_command_config_option` if you need different options for building the final image.

Build steps
===========

There are only three basic steps:

.. figure:: /images/builtin-build-system.svg
    :alt: Built-in build system
    :width: 500

    The steps LabTest's built-in build system goes through to generate a Docker image.

1. :ref:`builtin_build_check_out_code`.
2. :ref:`builtin_build_build_the_application`.
3. :ref:`builtin_build_build_the_docker_image`.


.. _builtin_build_check_out_code:

Check out code
==============

This step performs a shallow clone of the repo specified in :ref:`code_repo_url_config_option`. It uses a machine user to make this process easy to manage, and requires :ref:`initial setup<setting_up_the_builtin_build_process>`.

When updates are requested, the cloned repository simply updates the code.


.. _builtin_build_build_the_application:

Build the application
=====================

Most web apps today require some compilation and building in order to be ready to deploy. To allow for multiple applications to build without conflict, we use a pre-built Docker container with all the tools required.

Docker containers are immutable; any changes made in the container are gone the next time you run the container. The app building process *needs* to make lasting changes, however. In order to do this, we need to mount the checked out code into the container.

.. figure::  /images/build-environment.svg
    :alt: Build environment with mounted volume
    :width: 400

    The build container mounting the checked out code to the container's ``/build`` directory. Any changes made to the ``/build`` directory affect the checked out code.

When we do this, changes made to the mounted directory within the container are made outside the container.


.. _builtin_build_build_environment:

Build environment
-----------------

The :ref:`app_build_image_config_option` setting specifies the Docker image to use as a build environment. This environment should have all the tools you need pre-installed. We suggest choosing one of Shippable's `publicly available images`_ that fits your environment.

.. table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: auto

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

You can also create your own custom environments, and specify them instead.

So for a node.js application, you would set ``app_build_image: drydock/u16nodall``\ .

.. _publicly available images: http://docs.shippable.com/platform/runtime/machine-image/ami-overview/


.. _builtin_build_build_command:

Build command
-------------

This is the command the LabTest runs inside the build environment to complete the build process. We recommend creating a simple script in your code repository to run the commands. For example:

.. code-block:: bash
    :caption:   A simple ``buildapp`` bash script for a node.js application

    #!/bin/bash

    nvm use 8
    yarn install
    yarn run build

You would set ``app_build_script: ./bin/buildapp``\ , assuming that you made the script executable and put it in the ``bin`` directory of your code repository.

Results
-------

After LabTest runs your build command inside your build environment, everything should be ready to build the Docker image.


.. _builtin_build_build_the_docker_image:

Build the Docker image
======================

To build the Docker image, LabTest runs the command specified in :ref:`container_build_command_config_option`\ . The default is usually fine. The image is stored on the Laboratory server, which makes running and updating it a bit faster.
