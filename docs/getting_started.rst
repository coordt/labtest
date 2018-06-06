===============
Getting Started
===============

LabTest has three different parts: the laboratory, the project configuration and the client that runs on your machine.

What do you need to do?

- :ref:`I just need to get it working on my machine<getting_started:setting up your local machine>`
- :ref:`I need to get my project ready<reference/setting_up_your_project:setting up your project>`
- :ref:`I need a laboratory<admin/setting_up_the_lab:Setting up the laboratory>`


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

- SSH bastion DNS name or IP address
- The test server IP address (it is a non-routable IP address, like 10.x.x.x)
- Your user name. If your username contains ``+``\ , ``=``\ , ``,``\ , or ``@`` you need to convert a few characters:

  - ``+`` to ``.plus.``
  - ``=`` to ``.equal.``
  - ``,`` to ``.comma.``
  - ``@`` to ``.at.``

For this example:

- **SSH bastion IP address:** ``111.222.111.222``
- **Test server IP address:** ``10.20.3.3``
- **User name:** ``corey.oordt.at.boston.gov`` (converted from ``corey.oordt@boston.gov``\ )

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
