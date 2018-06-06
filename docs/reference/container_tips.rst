==============
Container Tips
==============


Dockerfile tips
===============

.. contents::
    :local:


Pass release information to the container build
-----------------------------------------------

Docker allows you to pass build-time arguments with the ``--build-arg <varname>=<value>`` flag. These are referenced in the Dockerfile using the ``ARG`` instruction.

You can use these to write release information to the image so it is retrievable during runtime. Then it is easy to determine exactly what code you are looking at in a given environment.

.. code-block:: docker
    :caption: Converting Docker build arguments into environment variables and writing the info to the image filesystem.

    ARG RELEASE
    ARG APP_NAME
    ARG INSTANCE_NAME
    ARG BRANCH_NAME
    ENV RELEASE=${RELEASE:-FORGOT_BUILD_ARG_RELEASE} \
        APP_NAME=${APP_NAME:-FORGOT_BUILD_ARG_APP_NAME} \
        INSTANCE_NAME=${INSTANCE_NAME:-FORGOT_BUILD_ARG_INSTANCE_NAME} \
        BRANCH_NAME=${BRANCH_NAME:-FORGOT_BUILD_ARG_BRANCH_NAME}
    RUN echo "{\"APP_NAME\": \"$APP_NAME\", \"INSTANCE_NAME\": \"$INSTANCE_NAME\", \"RELEASE\": \"$RELEASE\"}" > /pub/RELEASE.txt




Entrypoint tips
===============

.. contents::
    :local:


Use ``echo`` to help debugging
------------------------------

When you are trying to figure out why something is not working correctly when you run your Docker image, all you have is the logged output. Be generous with some ``echo`` statements to give information about what is going on.

.. code-block:: bash
    :caption: Using ``echo`` to indicate which branch of an ``if`` statement was taken. It is clear if the logs show ``Starting Gunicorn`` that the ``DEBUG`` environment variable was not ``True``\ .

    if [ "$DEBUG" == "True" ]; then
        echo "DEBUG MODE: Starting Waitress"
        waitress-serve --unix-socket=$HOMEDIR/gunicorn.sock --expose-tracebacks conf.docker_wsgi:application
    else
        echo "Starting Gunicorn"
        gunicorn --preload --config $GUNICORNCONF conf.docker_wsgi:application
    fi

.. code-block:: bash
    :caption: Using ``echo`` to show an unrecognized value. Both the unrecognized value and the fact it was unrecognized will show in the logs.

    case "$SITE" in
        en)
            echo "Using default English configuration"
            ;;
        es)
            echo "Copying over Spanish nGinx configuration"
            cp $HOMEDIR/sites/es/conf/nginx-core.conf /etc/nginx/nginx.conf
            ;;
        de)
            echo "Copying over German nGinx configuration"
            cp $HOMEDIR/sites/de/conf/nginx-core.conf /etc/nginx/nginx.conf
            ;;
        fr)
            echo "Copying over French nGinx configuration"
            cp $HOMEDIR/sites/fr/conf/nginx-core.conf /etc/nginx/nginx.conf
            ;;
        *)
            echo "I don't recognize SITE=$SITE"
            ;;
    esac


Detect overridden commands
--------------------------

In order to do this properly, you must use the *exec* form of ``ENTRYPOINT`` in your Dockerfile. This means your ``ENTRYPOINT`` looks like::

    ENTRYPOINT ["executable", "param1", "param2"]

Command line arguments to ``docker run <image>`` will be appended after all elements in an exec form ``ENTRYPOINT``\ , and will override all elements specified using ``CMD``\ .

With that in place, you can use the ``$#`` built-in ``bash`` variable to see if additional command-line arguments were passed.

.. code-block:: bash
    :caption: If ``$#`` is not 0, extra command-line arguments were passed.

    if [ $# -gt 0 ]; then
        echo "Running overridden command $@"
        exec $@
    else
        echo "Normal operation"
        # Do whatever that is
    fi
