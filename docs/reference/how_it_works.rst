============
How it Works
============

There are two parts to "how it works:"

- **The Laboratory.** This is the server setup that isolates and runs the experiments.
- **Experiments.** These are semi-public, semi-independent deployments of a version of a web site or app.


The Laboratory
==============

The laboratory environment is completely under your control and design. LabTest only requires SSH access, Docker, and `Nginx Proxy`_. You should also isolate this environment from other evironments and make it easily rebuildable.

Because this is a test environment, things will go wrong. You do not want an accident to harm another environment. This is also handy for security reasons. Since the developers will have SSH access to the test server, you want to limit the amount of damage a developer can accidentally inflict.

If something goes wrong, make it easy to scrap everything and rebuild from scratch. While rebuilding the environment might be inconvenient, it is easier than debugging what changed in the developer playground.

.. _nginx proxy: https://github.com/jwilder/nginx-proxy

The Laboratory ecosystem
------------------------

.. figure:: /_images/laboratory-ecosystem.svg
    :alt: The LabTest laboratory ecosystem
    :class: uk-margin-top

    The Laboratory ecosystem includes many parts to work correctly.

**SSH.** Underlying LabTest's automation is `Fabric`_, a Python library for running commands over SSH. All commands (even commands that could be run locally) are run via SSH on the Laboratory server. This allows you to easily manage permissions based on the server from which the request is made.

**Default user.** Commands that require user-specific authentication, such as Git commands, are made by ``su``\ -ing as a default user. This allows you to manage the SSH keys in one place.

**App names.** App names provide a method of isolating one project from another. An app name is equal to a Git repository.

**Experiment name vs. branch name.** Typically the name of the experiement is the same as the branch. This does not need to be the case.

**Docker containers.** Each experiment is run in a Docker container to isolate it from other experiments.

**Docker networks.** Each experiment has its own Docker network.

**Nginx Proxy.** One crux of the routing system is `Nginx Proxy`_'s ability to automatically add and route Docker containers as they spin up. Nginx Proxy runs as a Docker container and LabTest automatically adds Nginx Proxy to each experiment's Docker network.

**Splashpage.** This is a fallback page that is displayed when the host of an incoming request isn't recognized by Nginx Proxy. This is also helpful in returning a 200 response for health checks.

**OS services.** LabTest creates a Systemd service for every Docker container LabTest creates (app containers and backing services). This allows for independent starting and stopping and ensures the services come up upon a restart.

**Defaults and state.** While LabTest tries to be as stateless as possible, there are cases where it is necessary. State is provided by "state providers," a pluggable system for providing state. Defaults for provisioning backing services are stored in state and managed by you.

**Service providers.** A service provider manages the provisioning of backing services in a specific way, such as using Docker to provision a MySQL server. Service providers is also a pluggable system. All service providers run their provisioning commands from the Laboroatory server.

**Secret providers.** There are cases where you need to have private information, such as API keys, available for your experiments. A secret provider (again, a pluggable system) provides a method for encrypting a secret so you can store it in the LabTest configuration in your project. The secret is decrypted on the Laboratory server when needed.


.. _fabric: http://www.fabfile.org/

Experiments
===========

An experiment is a version (branch) of your code running in a Docker container on the test server. Each experiment gets its own DNS name, based on the ``VIRTUAL_HOST`` environment variable set on the Docker container.


Creating an experiment
----------------------

Creating an experiment is based on the idea of a mini-deployment using a Docker container. Each experiment has three parts: the application name, the branch name and the instance name. The application name is the name of the project or application. This provides a namespace for the instance names. If you are testing multiple applications, you might have branches with the same name across the different projects.

.. figure:: /_images/test-instance-steps.svg
    :alt: Steps for making an experiment

    The steps LabTest goes through when creating an experiment

Typically the instance name is the same as the branch name, but they don't have to be. You can have two experiments using the same branch, but with different instance names.

**Create experiment space.** The step creates a space to store files it might need. The space is at ``/testing/<app name>/<instance name>``\ .

**Trigger build.** The result of this step is a compiled Docker image. LabTest has a :ref:`built-in process <reference/builtin_build_process:Built-in build process>`\ , or you can use your own existing process that generates the image.

**Create container from image.** There are two parts to this: creating an environment file and creating the container. The environment file is automatically generated from the values in :ref:`configuration:environment`, plus a few extras:

- ``VIRTUAL_HOST`` is created from the :ref:`configuration:host_name_pattern` and :ref:`configuration:test_domain`\ .
- ``APP_NAME`` is :ref:`configuration:app_name`\ .
- ``INSTANCE_NAME`` is name of the test experiment.
- ``BRANCH_NAME`` is name of the branch.

The container is created and named using the `docker create`_ command. This allows us to start, stop and restart the container as an Systemd service.

**Create backing services.** *Coming soon!* This step will set up any backing services you need, such as databases and caches.

**Create OS Service.** This step creates Systemd services to start and stop the containers. It makes sure they are started in case of a reboot of the machine as well.

.. _docker create: https://docs.docker.com/engine/reference/commandline/create/

Experiment routing
------------------

Since we want the experiments available via the internet, we need a simple dynamic way to manage the DNS. A wildcard DNS entry will route traffic for any subdomain to a specific address. So, if we say "any address in the ``test.example.com`` subdomain routes to the test server," then the test server can decide how to route the traffic.

When the Docker container for an experiment runs, it can tell nginx proxy to route all traffic for ``foo.test.example.com`` to it. There is also a container that handles any unknown traffic and displays a splash page.

.. figure:: /_images/test-server.svg
    :alt: How experiment traffic is routed

    Experiment traffic is routed via ``nginx-proxy`` to the correct experiment via a wildcard DNS name.
