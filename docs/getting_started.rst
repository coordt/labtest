===============
Getting Started
===============

LabTest has three different parts: the laboratory, the project configuration and the client that runs on your machine.

What do you need to do?

- :ref:`I just need to get it working on my machine<getting_started:setting up your local machine>`
- :doc:`I need to get my project ready</reference/setting_up_your_project>`
- :doc:`I need a laboratory</tutorials/setting_up_a_lab>`


Setting up your local machine
=============================

This is a one-time process. It installs the Lab Test package and configures your machine to easily talk to the test server.

There are two things you need to do: install the LabTest client and get access to the Laboratory server.

Install labtest
===============

First we :ref:`install <install_stable>` the Lab Test command line package:

.. code-block:: console

    $ pip install labtest

At this point you should be able to run the command ``labtest``\ :

.. code-block:: console
    :caption: Testing your LabTest client install

    $ labtest
    Usage: labtest [OPTIONS] COMMAND [ARGS]...

      Console script for labtest

    Options:
      -c, --config PATH  Alternate configuration file.
      -v, --verbose      Show verbose output.
      --help             Show this message and exit.

    Commands:
      check-config  Check the configuration and output any errors
      create        Create a test instance on the server
      delete        Delete a test instance on the server
      encrypt       Encrypt a secret
      list          Delete a test instance on the server
      update        Delete a test instance on the server
      version       Display the current labtest client version

If you get ``Command not found`` on Mac OS X or Linux, you might need to edit the ``~/.bashrc`` file in your home folder and add the following at the bottom of the file:

.. code-block:: bash
    :caption: ``~/.bashrc`` addition

    export PATH="$HOME/.local/bin:$PATH"

For Windows, it depends on the version. `This article from Computer Hope`_ can help. You will need to append ``%APPDATA%Python/bin`` to your ``Path`` variable.

.. _this article from computer hope: https://www.computerhope.com/issues/ch000549.htm


Accessing the Laboratory
========================

.. note:: Gaining access to your Laboratory depends on how it is set up. Contact your administrator for the specific instructions.

This will walk you through an example setup using the default laboratory Cloud Formation configuration for AWS.

You will need your public SSH key. This is used for authenticating.


AWS account user
----------------

You need a user configured in AWS IAM. No specific permissions are required for each user by LabTest. It uses IAM and the SSH key for authentication.

To get your public SSH configured with IAM, :doc:`follow the instructions</admin/setting_up_users>`.


Configure SSH
-------------

To set up your SSH configuration. We need a few bits of information:

- SSH bastion DNS name or IP address
- The test server IP address (it is a non-routable IP address, like 10.x.x.x)
- Your user name.

If your username contains ``+``\ , ``=``\ , ``,``\ , or ``@`` you need to convert a few characters:

- ``+`` to ``.plus.``
- ``=`` to ``.equal.``
- ``,`` to ``.comma.``
- ``@`` to ``.at.``

For this example:

- **SSH bastion public IP address:** ``111.222.111.222``
- **Test server private IP address:** ``10.20.3.3``
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

.. note:: If the location of the private key is not at ``~/.ssh/id_rsa`` then change the ``IdentityFile`` path in both places.


With that in place, you should be able to :command:`ssh` to the test server:

.. code-block:: console
    :caption: SSH'ing to the test server

    $ ssh test
    Last login: Sun May  6 15:18:17 2018 from ip-10-20-2-2.ec2.internal

           __|  __|_  )
           _|  (     /   Amazon Linux 2 AMI
          ___|\___|___|

    https://aws.amazon.com/amazon-linux-2/
    No packages needed for security; 56 packages available
    Run "sudo yum update" to apply all updates.
    [corey.oordt.at.boston.gov@ip-10-20-3-3 ~]$

You can disconnect by typing :kbd:`control-d` or :kbd:`exit`.
