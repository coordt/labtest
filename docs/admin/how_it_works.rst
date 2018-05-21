============
How it Works
============

There are two parts to "how it works:"

- **The Laboratory.** This is the server setup that isolates and runs the experiments.
- **Experiments.** These are semi-public, semi-independent deployments of a version of a web site or app.


The Laboratory
--------------

The laboratory environment:

- Should be isolated from other environments (e.g. production)
- Should be easily rebuildable from scratch
- Should have access to test versions of all services you may need
- Should be accessible by developers via SSH

Isolated Laboratory
~~~~~~~~~~~~~~~~~~~

Because this is a test environment, things will go wrong. You do not want an accident to harm another environment. This is also handy for security reasons. Since the developers will have SSH access to the test server, you want to limit the amount of damage a hacker could do if you are compromised.

Easily Rebuildable
~~~~~~~~~~~~~~~~~~

If something goes wrong, make it easy to scrap everything and rebuild from scratch. While rebuilding the environment might be inconvenient, it is easier than debugging what changed in the developer playground.

Access to test versions of services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your web stack requires a database, you will need to have at least one database server available. Any other services, such as low-level caches or search indexes, need test versions as well.

Accessible by developers via SSH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary reason is that it is via SSH that the commands will communicate to set up each test instance. The other is that there are occasions when a developer having access to a production-like environment is advantageous.

Example setup
~~~~~~~~~~~~~

This setup shows an example setup created through :ref:`setting_up_the_laboratory`\ .

.. image:: /images/test-infrastructure.svg

- :abbr:`VPC (Virtual Private Cloud)`
- SSH Bastion
- :abbr:`IAM (Identity and Access Management)` for public key and access management
- Secret Provider
- Test Server
- Wildcard :abbr:`DNS (Domain Name Service)` Entry

With the exception of the wildcard DNS entry, the rest can be set up and customized in AWS via Cloud Formation templates.

**VPC.** The Virtual Private Cloud is a logically isolated section of the AWS Cloud. This is the isolation part of our environment. We use a `cloud formation template`_ from `Widdix`_ to create this.

**SSH Bastion.** A secure shell bastion is an entrance to monitor and manage access to servers that don't have SSH publicly enabled. We use an `SSH bastion template`_ from `Widdix`_ to create this.

**IAM public key management.** Widdix has a great article about `managing SSH access through IAM`_\ . Basically you add the user's public SSH key to their IAM profile, and the SSH bastion checks it when they attempt to log in.

**Secret Provider.** This is an AWS Lambda function that generates and stores secrets for Cloud Formation templates. It is created using the `Binxio cfn-secret-provider`_ template. This service is used to generate public and private RSA keys for the default ``ec2-user`` on the Test Server. This allows you to create a machine user on GitHub to check out code repos.

**Test Server.** The test server is an :abbr:`EC2 (Elasic Compute Cloud)` instance running Docker and `nginx proxy`_\ . Nginx proxy is an `automated reverse proxy for Docker containers`_\ . It will route any connection on port 80 to the appropriate running Docker container with a ``VIRTUAL_HOST`` environment variable set.

An :abbr:`EBS (Elastic Block Store)` volume is connected, but not mounted, for Docker to store the containers (via the `devicemapper driver`_\ ).

We created a `test server template`_ to create this server.

**Wildcard DNS entry.** Since we want the experiments available via the internet, we need a simple dynamic way to manage the DNS. A wildcard DNS entry will route traffic for any subdomain to a specific address. So, if we say "any address in the ``test.example.com`` subdomain routes to the test server," then the test server can decide how to route the traffic.

When the Docker container for an experiment runs, it can tell nginx proxy to route all traffic for ``foo.test.example.com`` to it.

.. image:: /images/test-server.svg

.. _cloud formation template: http://templates.cloudonaut.io/en/stable/vpc/
.. _widdix: https://cloudonaut.io/
.. _ssh bastion template: http://templates.cloudonaut.io/en/stable/vpc/#ssh-bastion-hostinstance
.. _managing ssh access through iam: https://cloudonaut.io/manage-aws-ec2-ssh-access-with-iam/
.. _devicemapper driver: https://docs.docker.com/storage/storagedriver/device-mapper-driver/
.. _binxio cfn-secret-provider: https://github.com/binxio/cfn-secret-provider
.. _nginx proxy: https://github.com/jwilder/nginx-proxy
.. _automated reverse proxy for docker containers: http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/
.. _test server template: https://github.com/CityOfBoston/labtest/blob/master/infrastructure/cloudformation/testserver.yaml


.. _how_it_works_experiments:

Experiments
-----------

An experiment is a version (branch) of your code running in a Docker container on the test server. Each experiment gets its own DNS name, based on the ``VIRTUAL_HOST`` environment variable set on the Docker container.


Creating an experiment
~~~~~~~~~~~~~~~~~~~~~~

Creating an experiment is based on the idea of a mini-deployment using a Docker container. Each experiment has three parts: the application name, the branch name and the instance name. The application name is the name of the project or application. This provides a namespace for the instance names. If you are testing multiple applications, you might have branches with the same name across the different projects.

.. figure:: /images/test-instance-steps.svg
    :alt: Steps for making an experiment

    The steps LabTest goes through when creating an experiment

Typically the instance name is the same as the branch name, but they don't have to be. You can have two experiments using the same branch, but with different instance names.

**Create experiment space.** The step creates a space to store files it might need. The space is at ``/testing/<app name>/<instance name>``\ .

**Trigger build.** The result of this step is a compiled Docker image. Test Lab has a :ref:`built-in process <builtin_build_process>`\ , or you can use your own existing process that generates the image.

**Create container from image.** There are two parts to this: creating an environment file and creating the container. The environment file is automatically generated from the values in :ref:`environment_config_option`, plus a few extras:

- ``VIRTUAL_HOST`` is created from the :ref:`host_name_pattern_config_option` and :ref:`test_domain_config_option`\ .
- ``APP_NAME`` is :ref:`app_name_config_option`\ .
- ``INSTANCE_NAME`` is name of the test instance.
- ``BRANCH_NAME`` is name of the branch.

The container is created and named using the `docker create`_ command. This allows us to start, stop and restart the container as an Systemd service.

**Create backing services.** *Coming soon!* This step will set up any backing services you need, such as databases and caches.

**Create OS Service.** This step creates Systemd services to start and stop the containers. It makes sure they are started in case of a reboot of the machine as well.

.. _docker create: https://docs.docker.com/engine/reference/commandline/create/
