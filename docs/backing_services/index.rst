===========================
Specifying backing services
===========================

Backing services are external services your project needs in order to work properly, such as a database, a cache, or a search index.

Pre-existing Services
=====================

You can manually set up shared backing services in your laboratory environment. To use these services in your experiments, you simply have to provide the appropriate environment variables in the configuration. For example, if you are sharing a Memcached server, you might add:

.. code-block:: yaml
    :caption: Specifying shared services in the configuration

    labtest:
      environment:
        - MEMCACHE_URL=10.20.4.121:11211

Then your project can use the environment variable ``MEMCACHE_URL`` to configure itself in the experiment.


On-Demand Services
==================

You can also have LabTest manage your backing services for each experiment. LabTest will provision the service and set environment variables in your experiment's container.

On-demand services are specified in the ``services`` section of the experiment configuration. The ``services`` is organized by the name of the backing service, and each backing service will require at least three parameters: ``provider``\ , ``service``\ , and ``provision_type``\ . The parameters ``shared_instance_name`` and ``shared_app_name`` are required for shared provision types.

.. code-block:: yaml
    :caption:   Sample service configuration

    labtest:
      services:
        mydb:
          provider: docker
          service: mysql
          provision_type: independent

In this example ``docker`` will provision an ``independent`` ``mysql`` service named ``mydb``\ .


``provider``
------------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``True``
    * - Acceptable values:
      - ``docker``

A ``provider`` is the method of hosting the backing service you need. Right now only ``docker`` is supported, but others will be possible in the future.

``service``
-----------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``True``
    * - Acceptable values:
      - Depends on the services provided by the provider

The ``service`` is the type of service to provision, such as MySQL, Redis, or ElasticSearch. Different providers can provision different services. Check out the :ref:`backing_services_providers` to see the options.


.. _backing_services_provision_types:

``provision_type``
------------------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``independent``
    * - Required:
      - ``False``
    * - Acceptable values:
      - ``communal``\ , ``independent``\ , or ``shared``

LabTest supports three types of provisioning of backing services: ``communal``\ , ``independent``\ , and ``shared``\ .

In a *communal* server provisioning, only one server is running, but each experiment might have their own independent part of it, depending on the service type. For example, in a communal database service, there is one server instance, but LabTest will manage an exclusive database on that server for each experiment. LabTest will provision the server instance, if it doesn't exist, and will never destroy it. Individual databases are created and destroyed with the experiements.

In an *independent* server provisioning, each experiment has their own service instance. LabTest creates and destroys the server instance with the experiment.

In a *shared* server provisioning, an experiment uses the exact service instance as another experiment. No provisioning is done at all. You will also have to specify the ``shared_experiment_name`` and possibly ``shared_app_name`` so LabTest can retrieve the appropriate configuration information.


``shared_experiment_name``
--------------------------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - Only if ``provision_type`` is ``shared``
    * - Acceptable values:
      - Name of any other experiment running

This parameter is only required if you specify ``provision_type: shared``\ . The value is the name of the experiment responsible for the database.


``shared_app_name``
-------------------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - Current app name
    * - Required:
      - ``False``
    * - Acceptable values:
      - Name of any other app running an experiment

You only need to specify this parameter if you need to share a database with another application for some reason. This value defaults to the same app name as your experiment. You need to set the ``shared_instance_name`` as well.


.. _backing_services_providers:

Providers
=========

.. toctree::
   :maxdepth: 2

   docker
   aws
