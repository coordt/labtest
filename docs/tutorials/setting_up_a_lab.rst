=======================
Setting up a laboratory
=======================

The Laboratory is the server or cloud set up that you manage. LabTest only needs SSH access and Docker available. This tutorial walks you through an example setup using Amazon Web Services and CloudFormation.

.. figure:: /_images/test-infrastructure.svg
    :alt: A basic diagram of the Example Laboratory environment we will set up.
    :width: 500

    A basic diagram of the Example Laboratory environment we will set up.

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

.. image:: /_images/test-server.svg

.. _cloud formation template: http://templates.cloudonaut.io/en/stable/vpc/
.. _widdix: https://cloudonaut.io/
.. _ssh bastion template: http://templates.cloudonaut.io/en/stable/vpc/#ssh-bastion-hostinstance
.. _managing ssh access through iam: https://cloudonaut.io/manage-aws-ec2-ssh-access-with-iam/
.. _devicemapper driver: https://docs.docker.com/storage/storagedriver/device-mapper-driver/
.. _binxio cfn-secret-provider: https://github.com/binxio/cfn-secret-provider
.. _nginx proxy: https://github.com/jwilder/nginx-proxy
.. _automated reverse proxy for docker containers: http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/
.. _test server template: https://github.com/CityOfBoston/labtest/blob/master/infrastructure/cloudformation/testserver.yaml
