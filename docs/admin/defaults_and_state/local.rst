====================
Local state provider
====================

You can provide very basic state management on the labratory server. The ``provider`` is set to ``local`` for all these state services.

Local Script
------------

You can specify a script or command local to the Laboratory server to execute and return the requested state. The ``service`` is ``script`` it requires a ``command`` key with the command to execute.

.. code-block:: javascript
    :caption:   Configuration for a local script state provider

    {
        "provider": "local",
        "service": "script",
        "options": {
            "command": "/testing/bin/get-state"
        }
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


The script should accept a hierarchical key (``/a/b/c``\ ) and return a value to standard out. It should follow the discovery path as described in :ref:`admin/defaults_and_state/index:state keys and values`. Errors are treated as if the key was not found.

Here is a simple Bash script for example:

.. code-block:: bash
    :caption: ``get-state`` script for getting state in a directory

    #!/bin/bash

    STATE_PATH=/testing/labteststate
    STATE_FILE=""

    search_up() {
        # 1. look for exact match
        # 2. Add /default to the end
        # 3. Loop until getting to STATE_PATH:
        #    Check for existence
        #    go up a level and add /default
        LOOK=${STATE_PATH%/}/${1#/}
        local TOP=${STATE_PATH%/}
        if [[ -f $LOOK ]]
        then
            STATE_FILE=$LOOK
            return
        fi
        while [[ $LOOK != $TOP ]]; do
            LOOK=${LOOK%/}/default
            if [[ -f $LOOK ]]
            then
                STATE_FILE=$LOOK
                return
            fi
            LOOK=${LOOK%/*/default}
        done
        STATE_FILE=""
        return
    }

    search_up "$1"

    if [[ -n $STATE_FILE ]]
    then
        cat $STATE_FILE
    fi
