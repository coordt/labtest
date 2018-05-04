=============
Configuration
=============

Automatic configuration files
=============================

Most code repositories have enough configuration files, and we didn't want to add *another* configuration file. Lab Test will automatically look for its configuration information  in several files already in your repository, under a ``labtest`` section:

    - ``.labtest.yml``
    - ``setup.cfg``
    - ``package.json``

Alternate configuration files
=============================

You can alternatively pass the configuration file to Lab Test at the command line with the ``--config`` option. Lab Test supports ``.ini``, ``.yml/.yaml``, and ``.json`` formats.


.. literalinclude:: ../tests/fixtures/config.ini
   :language: ini
   :caption: Example ``.ini`` configuration


.. literalinclude:: ../tests/fixtures/config.yml
   :language: yaml
   :caption: Example ``.yaml`` configuration


.. literalinclude:: ../tests/fixtures/config.json
   :language: json
   :caption: Example ``.json`` configuration


Required configuration options
==============================

There are several options that are required in order for Lab Test to work correctly.

.. _hosts_config_option:

host
----

The DNS name, IP address or SSH config ``Host`` of the test server.

.. _code_repo_url_config_option:

code_repo_url
-------------

The URL of the code repository to check out.

.. _env_template_config_option:

env_template
------------

The code repository-relative path of the environment template.

Optional configuration options
==============================

.. _app_name_config_option:

app_name
--------

The name of the application. It defaults to the name of the project directory.


.. _use_ssh_config_config_option:

use_ssh_config
--------------

Use your local SSH config when connecting


.. _provider_config_option:

provider
--------

This is to extend how Lab Test can talk to different Docker container repositories. Currently only aws is supported.


.. _app_build_image_config_option:

app_build_image
---------------

The Docker image to use to build the app. `Shippable`_ has some great `images publicly available`_\ . Here is their `docker page`_\ . This is required if you want to build the application on the test server. Also set the :ref:`app_build_command_config_option` option.

.. _shippable: https://www.shippable.com/
.. _images publicly available: http://docs.shippable.com/platform/runtime/machine-image/ami-overview/
.. _docker page: https://hub.docker.com/u/drydock/


.. _app_build_command_config_option:

app_build_command
-----------------

The script or command to run to build the app within the Docker image. This is required if you want to build the application on the test server. Also set the :ref:`app_build_image_config_option` option.

This command is executed from within the container and in the project's directory.

For example:

.. code-block:: yaml

    app_build_command: npm run build

If you require several commands, you will need to create a script in your repository that we can run:

.. code-block:: yaml

    app_build_command: ./bin/build_my_app

If the execute bit is not set you must include the name of the program to execute the script, for example:

.. code-block:: yaml

    app_build_command: python ./config/build.py

or:

.. code-block:: yaml

    app_build_command: bash bin/build_my_app


.. container_build_command_config_option:

container_build_command
-----------------------

What command to use to build the container for your app.

Lab Test appends your command to a script that sets the following variables: ``$APP_NAME``, ``$INSTANCE_NAME``, ``$BRANCH_NAME``, and ``$RELEASE``.

The default build command is (formatted for clarity):

.. code-block:: bash

    docker build \
        -t $APP/$INSTANCE \
        --build-arg RELEASE=$RELEASE \
        --build-arg APP_NAME=$APP \
        --build-arg BRANCH_NAME=$BRANCH \
        --build-arg INSTANCE_NAME=$INSTANCE \
        .

If you override the docker build command, you *must* still tag it with ``$APP/$INSTANCE`` or the remaining commands will fail.

If your ``Dockerfile`` doesn't use the default ``--build-arg``\ s passed, they are ignored.
