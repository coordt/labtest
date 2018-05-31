=======================
Docker service provider
=======================

Docker can provision basic services in containers that are secure and independent. They all have their ``provider`` set to ``docker``\ .

Databases
=========

MySQL
-----

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Provider:
      - ``docker``
    * - Service:
      - ``mysql``
    * - Provision types:
      - ``independent`` or ``shared``
    * - Options:
      - :ref:`docker:initial_data_source`, :ref:`docker:image`, :ref:`docker:commands`, and :ref:`docker:environment`


.. code-block:: yaml
    :caption: Specifying a MySQL database backing service in the configuration

    labtest:
      services:
        mydb:
          provider: docker
          service: mysql
          provision_type: independent
          options:
            initial_data_source: "/backups/bostongov/"
            image: "mysql:5.6"
            wait_for_service: false
            wait_attempts: 6
            wait_timeout: 60
            commands:
              - "--character-set-server=utf8mb4"
              - "--collation-server=utf8mb4_unicode_ci"
            environment:
              - "MYSQL_ALLOW_EMPTY_PASSWORD=true"
              - "MYSQL_DATABASE=drupal"


.. _docker:initial_data_source:

``initial_data_source``
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``False``
    * - Acceptable values:
      - Directory or path

This parameter uses the default database restoration tool for the database type to restore a file to the database. If the value is a directory, LabTest uses the most recent file in that directory. If the value is a file, LabTest uses the indicated file.

You will need to specify the ``MYSQL_DATABASE=<value>`` ``environment`` variable as well.

.. _docker:image:

``image``
~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``mysql``
    * - Required:
      - ``False``
    * - Acceptable values:
      - One of the values of the of the `official MySQL Docker image`_ or another Docker image based on it.

This is the MySQL Docker image to use for the service.

.. warning::

    If you do not use an official MySQL image, some provisioning functions might not work, such as the ``initial_data_source``\ .

.. _official MySQL Docker image: https://hub.docker.com/_/mysql/


.. _docker:wait_for_service:

``wait_for_service``
~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``False``
    * - Required:
      - ``False``
    * - Acceptable values:
      - ``True`` or ``False``

Should we wait to make sure this service is running and accepting connections before continuing? If ``True``, it will attempt to connect up to :ref:`docker:wait_attempts` times or :ref:`docker:wait_timeout` seconds before giving up. LabTest uses an exponential wait between each attempt: 1 second, then 2 seconds, 4 seconds, 8 seconds, etc.

.. _docker:wait_attempts:

``wait_attempts``
~~~~~~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``6``
    * - Required:
      - ``False``
    * - Acceptable values:
      - Positive number

This is how many attempts to make before giving up on the service. It is closely tied to :ref:`docker:wait_timeout` in that there is a longer wait time between each attempt, which brings it closer to the ``wait_timeout``.


.. table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: auto

    =======  ================  ================
    Attempt  Min Elapsed Time  Pause after fail
    =======  ================  ================
    1        0 seconds         1 seconds
    2        1 seconds         2 seconds
    3        3 seconds         4 seconds
    4        7 seconds         8 seconds
    5        15 seconds        16 seconds
    6        31 seconds        32 seconds
    7        63 seconds        64 seconds
    8        127 seconds       128 seconds
    9        255 seconds       256 seconds
    10       511 seconds       512 seconds
    11       1023 seconds      1024 seconds
    12       2047 seconds      2048 seconds
    =======  ================  ================

Looking at the above table, it will take a minimum of 2047 seconds to make 12 attempts. That assumes that the attempt fails immediately. So with a `wait_timeout` of 60 seconds, you'll only get 6 attempts before the time runs out.


.. _docker:wait_timeout:

``wait_timeout``
~~~~~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``60``
    * - Required:
      - ``False``
    * - Acceptable values:
      - Positive integer

How long in seconds to wait before giving up.


.. _docker:commands:

``commands``
~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``False``
    * - Acceptable values:
      - A sequence of strings

Many configuration options can be passed as flags to ``mysqld``\ . This is a list of the strings to pass to ``mysqld``\ . See the section "Configuration without a cnf file" on the `official MySQL Docker image`_ page.


.. _docker:environment:

``environment``
~~~~~~~~~~~~~~~

.. list-table::
    :class: uk-table uk-table-striped uk-table-small
    :widths: 33 64
    :stub-columns: 1

    * - Default:
      - ``None``
    * - Required:
      - ``False``
    * - Acceptable values:
      - A sequence of strings

These environment variables are passed to the MySQL container to assist with configuration. The `MySQL documentation`_ has a list of valid environment variables. The `official MySQL Docker image`_ page also describes: ``MYSQL_ROOT_PASSWORD``\ , ``MYSQL_DATABASE``\ , ``MYSQL_USER``\ , ``MYSQL_PASSWORD``\ , ``MYSQL_ALLOW_EMPTY_PASSWORD``\ , ``MYSQL_RANDOM_ROOT_PASSWORD``\ , and ``MYSQL_ONETIME_PASSWORD``\ .

.. _mysql documentation: https://dev.mysql.com/doc/refman/5.7/en/environment-variables.html
