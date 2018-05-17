=======================
Docker service provider
=======================

Docker can provision basic services in containers that are secure and independent.

Databases
=========

MySQL
-----

This service accepts several additional parameters

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
            commands:
              - "--character-set-server=utf8mb4"
              - "--collation-server=utf8mb4_unicode_ci"
            environment:
              - "MYSQL_ALLOW_EMPTY_PASSWORD=true"
              - "MYSQL_DATABASE=drupal"

options
~~~~~~~

:Default: None
:Required: No
:Acceptable values: A mapping of options specified below
:Description: The ``options`` include all the configuration you need to make for the ``mysql`` service. Details of the options are described below.


initial_data_source
~~~~~~~~~~~~~~~~~~~

:Default: None
:Required: No
:Acceptable values: Directory or path
:Description: This parameter uses the default database restoration tool for the database type to restore a file to the database. If the value is a directory, LabTest uses the most recent file in that directory. If the value is a file, LabTest uses the indicated file.

    You will need to specify the ``MYSQL_DATABASE=<value>`` ``environment`` variable as well.

image
~~~~~

:Default: ``mysql``
:Required: No
:Acceptable values: One of the values of the of the `official MySQL Docker image`_ or another Docker image based on it.
:Description: This is the MySQL Docker image to use for the service.

.. warning:: If you do not use an official MySQL image, some provisioning functions might not work, such as the ``initial_data_source``\ .

.. _official MySQL Docker image: https://hub.docker.com/_/mysql/

commands
~~~~~~~~

:Default: None
:Required: No
:Acceptable Values: A sequence of strings
:Description: Many configuration options can be passed as flags to ``mysqld``\ . This is a list of the strings to pass to ``mysqld``\ . See the section "Configuration without a cnf file" on the `official MySQL Docker image`_ page.

environment
~~~~~~~~~~~

:Default: None
:Required: No
:Acceptable Values: A sequence of strings
:Description: These environment variables are passed to the MySQL container to assist with configuration. The `MySQL documentation`_ has a list of valid environment variables. The `official MySQL Docker image`_ page also describes: ``MYSQL_ROOT_PASSWORD``\ , ``MYSQL_DATABASE``\ , ``MYSQL_USER``\ , ``MYSQL_PASSWORD``\ , ``MYSQL_ALLOW_EMPTY_PASSWORD``\ , ``MYSQL_RANDOM_ROOT_PASSWORD``\ , and ``MYSQL_ONETIME_PASSWORD``\ .

.. _mysql documentation: https://dev.mysql.com/doc/refman/5.7/en/environment-variables.html
