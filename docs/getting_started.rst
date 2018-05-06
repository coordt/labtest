===============
Getting Started
===============

.. _setting_up_your_local_machine:

Setting up your local machine
=============================

This is a one-time process. It installs the Lab Test package and configures your machine to easily talk to the test server.

Install labtest
---------------

First we :ref:`install <install_stable>` the Lab Test command line package:

.. code-block:: console

    $ pip install labtest

Public key in IAM
-----------------

Make sure your public key was added to your AWS IAM account. Without that, you will not be able to SSH into anything.

Configure SSH
-------------

Let's set up our SSH configuration. We need a few bits of information:

* SSH bastion DNS name or IP address
* The test server IP address (it is a non-routable IP address, like 10.x.x.x)
* Your user name. If your username contains ``+``\ , ``=``\ , ``,``\ , or ``@`` you need to convert a few characters:

    - ``+`` to ``.plus.``
    - ``=`` to ``.equal.``
    - ``,`` to ``.comma.``
    - ``@`` to ``.at.``

For this example:

* **SSH bastion IP address:** ``111.222.111.222``
* **Test server IP address:** ``10.20.3.3``
* **User name:** ``corey.oordt.at.boston.gov`` (converted from ``corey.oordt@boston.gov``\ )

Now we add some lines to our ``~/.ssh/config`` file:

.. code-block:: none
    :caption: The addition to the ``~/.ssh/config`` file.

    Host bastion
    Hostname 111.222.111.222
    Port 22
    User corey.oordt.at.boston.gov
    IdentityFile ~/.ssh/id_rsa

    Host test
    Hostname 10.20.3.3
    User corey.oordt.at.boston.gov
    Port 22
    ProxyCommand ssh -A -T bastion nc %h %p
    IdentityFile ~/.ssh/id_rsa

With that in place, you should be able to :command:`ssh` to the test server:

.. code-block:: console
    :caption: SSH'ing to the test server

    $ ssh test
    Last login: Sun May  6 15:18:17 2018 from ip-10-20-2-195.ec2.internal

           __|  __|_  )
           _|  (     /   Amazon Linux 2 AMI
          ___|\___|___|

    https://aws.amazon.com/amazon-linux-2/
    No packages needed for security; 56 packages available
    Run "sudo yum update" to apply all updates.
    [corey.oordt.at.boston.gov@ip-10-20-10-41 ~]$

You can disconnect by typing :kbd:`control-d` or :kbd:`exit`.


Getting your code ready
=======================

Containerize it
---------------

If your app doesn't already have a ``Dockerfile`` and a way to build everything as a container, you need to adapt it.

This topic is too broad to go into here. You'll know you are ready when you can run something like::

    docker build -t myapp .
    docker run --rm -ti myapp

That means your container builds and runs locally.

.. _automating-the-app-build-process:

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
