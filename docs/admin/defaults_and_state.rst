========================
Default values and state
========================

LabTest tries to keep the amount of administration to a minimum. However, that doesn't work in every organization or scenario. There may come a time when your organization wants to tweak the way LabTest works.

Since LabTest is designed to be easy to destroy and rebuild, storing state on the Laboratory server isn't a good idea. Instead you can create a file on the Laboratory server (``/testing/state.json``\ ) that indicates where the state is stored.

When it state needed?
=====================

State is necessary to

- tell the client something it couldn't know, like which secret provider to use
- provide defaults for provisioning



.. _state_keys_and_values:

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

However, if you attempted to get the value for ``/services/docker/mysql/app-name1``\ , the state doesn't find ``app-name1`` under ``/services/docker/mysql/``\ . Next it looks for ``/services/docker/mysqlapp-name1/default`` and then ``/services/docker/mysql/default``, which it finds and returns.

For security reasons, the LabTest client has read-only privledges on the state. The method of writing the values is dependent on the state provider.


state.json
==========

This file configures LabTest's method for retrieving state. It should exist at ``/testing/state.json``\ . The only required key and value in ``state.json`` is ``provider``\ . All other keys and values are dependent on the provider.

Configuration
-------------

``provider``
~~~~~~~~~~~~

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


State providers
===============

Local Script
------------

You can specify a script or command local to the Laboratory server to execute and return the requested state. The ``provider`` is ``script`` and it requires a ``command`` key with the command to execute.

.. code-block:: javascript
    :caption:   Configuration for a local script state provider

    {
        "provider": "script",
        "command": "/testing/bin/get-state"
    }


``command``
~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``True`` if ``provider`` is ``script``
    * - Acceptable values:
      - String of a command to call


The script should accept a hierarchical key (``/a/b/c``\ ) and return a value to standard out. It should follow the discovery path as described in :ref:`state_keys_and_values`. Errors are treated as if the key was not found.

Here is a simple Bash script for example:

.. literalinclude:: ../../infrastructure/get-state
    :language: bash
    :caption: ``get-state`` script for getting state in a directory



AWS S3
------

S3 provides a flexible method for storing state information, since there are many ways for administrators to update it and secure it. The ``provider`` is ``s3``\ , and it requires a ``bucket`` key for the name of the bucket.


- local caching
    - look at local filesystem first, then query s3 and save it to local filesystem
    - should have a cron job to sync s3

.. code-block:: javascript
    :caption:   Configuration for an S3 state provider

    {
        "provider": "s3",
        "bucket": "labtest",
        "cache": true,
        "cache_path": "/testing/state/"
    }

``bucket``
~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``True`` if ``provider`` is ``s3``
    * - Acceptable values:
      - Name of an S3 bucket

This is the name of the S3 bucket that stores the state.

``cache``
~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``True``
    * - Required:
      - ``False``
    * - Acceptable values:
      - ``True`` or ``False``

LabTest can keep a local cache on the laboratory filesystem. This can speed up queries and reduce costs. LabTest will look in the cache first, and only download the state file if it doesn't exist.

You can even prime the cache using a cron job that syncronizes the S3 bucket to the local cache.

.. code-block:: console
    :caption: Command to syncronize the state from the S3 bucket to the local filesystem.

    $ aws s3 sync s3://mylabteststate /testing/state --delete


``cache_path``
~~~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``/testing/state/``
    * - Required:
      - ``False``
    * - Acceptable values:
      - A directory path

This is where LabTest will cache the documents it retrieves from the S3 bucket.
