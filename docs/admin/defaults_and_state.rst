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
      postgresql
        default
        shared
        app-name1
      mysql
        default
        shared
        app-name2

If you wanted to get the value for ``/services/postgresql/app-name1``\ , the state looks and sees there is a value for that.

However, if you attempted to get the value for ``/services/mysql/app-name1``\ , the state doesn't find ``app-name1`` under ``/services/mysql/``\ . Next it looks for ``/services/mysql/default``\ , which it finds and returns.

For security reasons, the LabTest client has read-only privledges on the state. The method of writing the values is dependent on the state provider.


state.json
==========

The only required key and value in ``state.json`` is ``provider``\ . All other keys and values are dependent on that value.


State providers
===============

Local Script
------------

*provider:* ``script``
*command:* ``<command>``

You can specify a script or command local to the Laboratory server to execute and return the requested state. The ``provider`` is ``script`` and it requires a ``command`` key with the command to execute.

The script should accept a hierarchical key (``/a/b/c``\ ) and return a value to standard out. Errors are treated as if the key was not found.

.. code-block:: javascript
    :caption:   Configuration for a local script state provider

    {
        "provider": "script",
        "command": "/testing/bin/get-state"
    }

Here is a simple Bash script for example:

.. literalinclude:: ../../infrastructure/get-state
    :language: bash
    :caption: ``get-state`` script for getting state in a directory



AWS S3
------

*provider:* ``s3``
*bucket:* ``<bucketname>``

S3 provides a flexible method for storing state information, since there are many ways for administrators to update it and secure it. The ``provider`` is ``s3``\ , and it requires a ``bucket`` key for the name of the bucket.

.. code-block:: javascript
    :caption:   Configuration for an S3 state provider

    {
        "provider": "s3",
        "bucket": "labtest"
    }


Default state provider
======================

LabTest attempts to use AWS S3 as a default state provider when you don't explicitly set a state provider. If LabTest doesn't see a ``state.json`` configuration file, it checks for an S3 bucket named ``labtest``\ . If the bucket exists and is accessible, it attempts to find its state there.
