===================
Amazon Web Services
===================

S3
==

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Provider:
      - ``aws``
    * - Service:
      - ``s3``
    * - Options:
      - :ref:`aws:bucket`, :ref:`aws:cache`, and :ref:`aws:cache_path`


S3 provides a flexible method for storing state information, since there are many ways for administrators to update it and secure it. This configuration requires a ``bucket`` key for the name of the bucket.

By default, local caching is turned on. This allows a bit less time querying S3. This service looks at local filesystem first. If the key is not found, it queries S3. If the key is found in S3, it saves it to local filesystem. You can also create a simple cron job and use the ``aws s3 sync`` command to improve performance.

.. code-block:: javascript
    :caption:   Configuration for an S3 state provider

    {
        "provider": "aws",
        "service": "s3",
        "options": {
          "bucket": "labtest",
          "cache": true,
          "cache_path": "/testing/state/"
        }
    }

.. _aws:bucket:

``bucket``
----------

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``True``
    * - Acceptable values:
      - Name of an S3 bucket

This is the name of the S3 bucket that stores the state.


.. _aws:cache:

``cache``
---------

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



.. _aws:cache_path:

``cache_path``
--------------

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
