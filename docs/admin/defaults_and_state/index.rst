========================
Default values and state
========================

LabTest tries to keep the amount of administration to a minimum. However, that doesn't work in every organization or scenario. There may come a time when your organization wants to tweak the way LabTest works.

Since LabTest is designed to be easy to destroy and rebuild, storing state on the Laboratory server isn't a good idea. Instead you can create a file on the Laboratory server (``/testing/state.json``\ ) that indicates where the state is stored.

State keys and values
=====================

Before we get into *how* the state data is stored, let's talk about *what* is stored. State is a hierarchical key-value store that allows for defaults and overrides. That means that you can request a very specific value, and the state will attempt to return the best fit, based on the hierarchy. That means walking up the hierarchy looking for a ``default`` key.

If you request the key ``/a/b/c``\ , the state actually looks for the first of:

1. ``/a/b/c``
2. ``/a/b/c/default``
3. ``/a/b/default``
4. ``/a/default``
5. ``/default``

This allows administrators to put in good defaults and override them for specific applications as necessary, and clients to ask for the most specific entry in one call, and get the best value.

Take this example:

.. code-block:: none
    :caption:   Example state hierarchy

    services
      docker
        postgresql
          default
          shared
          app-name1
        mysql
          default
          shared
          app-name2

.. figure:: /images/state-search-postgresql.svg
    :alt: Searching the state for /services/docker/postgresql/app-name1
    :width: 400

    Searching the state for /services/docker/postgresql/app-name1 finds it on the first attempt.

If you wanted to get the value for ``/services/docker/postgresql/app-name1``\ , the state looks and sees there is a value for that.

.. figure:: /images/state-search-mysql.svg
    :alt: Searching the state for /services/docker/mysql/app-name1
    :width: 400

    Searching the state for /services/docker/mysql/app-name1 finds it on the third attempt.

However, if you attempted to get the value for ``/services/docker/mysql/app-name1``\ , the state doesn't find ``app-name1`` under ``/services/docker/mysql/``\ . Next it looks for ``/services/docker/mysql/app-name1/default`` and then ``/services/docker/mysql/default``, which it finds and returns.

For security reasons, the LabTest client has read-only privledges on the state. The method of writing the values is dependent on the state provider.


When it state needed?
=====================

State is necessary to tell the client something it couldn't know, like which secret provider to use, and provide defaults for provisioning.

The defaults for provisioning allow you to control parameters when provisioning services in a cloud environment. The experiment will just for an independent MySQL server. The state can provide defaults that indicate the default ``DBInstanceClass`` is ``db.m1.small``\ . As shown in the example above, you can specify overrides for specific applications. If your ``app-name1`` requires a different ``DBInstanceClass`` or ``EngineVersion``\ , you can provide that information.


state.json
==========

This file configures LabTest's method for retrieving state. It should exist at ``/testing/state.json``\ . The only required keys and values in ``state.json`` is ``provider`` and ``service``\ . The ``options`` key is where configuration for the specified secret provider goes.


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
      - String of a state provider

A ``provider`` is the method of hosting the state you need. Right now only ``aws`` and ``local`` are supported, but others will be possible in the future.


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
      - Depends on the state services provided by the provider

The ``service`` is the type of state service to provision, such as S3, Redis, or Memcached. Different providers can provision different services. Check out the :ref:`state_providers` to see the options.


``options``
-----------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``False``
    * - Acceptable values:
      - A mapping of options for the provider/service combination

The ``options`` include all the configuration you need to provider state service offered by the provider. Details of the options available are described in the description of each service.


.. _state_providers:

State providers
===============

.. toctree::
   :maxdepth: 2

   local
   aws
