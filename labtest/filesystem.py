"""
Provides helpers for filesystem operations that extend Fabric's
"""
from io import BytesIO
from fabric.operations import get
from fabric.context_managers import hide
from fabric.api import env, run
# from fabric.contrib.files import exists


def get_file_contents(remote_path):
    """
    Reads the file contents into a buffer.

    The buffer is a BytesIO buffer, so it works for binary and text documents.

    For text documents, you will have to coerce it appropriately.

    Args:
        remote_path:  The path to the remote file

    Returns:
         A BytesIO buffer.
    """
    buffer = BytesIO()
    with hide('running'):
        get(local_path=buffer, remote_path=remote_path)

    return buffer


def create_dir(remote_path, owner=None, group='docker', mode=None):
    """
    Create a directory and the intermediate paths as required.

    The group will always be set to ``group``. The owner and mode will not be
    set unless specified

    Args:
        remote_path:  The remote directory path
        owner: The name of the user to set the owner of the directory
        group: The name of the group to set the group of the directory
        mode: The mode to set the directory, as a string
    """
    run('mkdir -p {}'.format(remote_path), quiet=env.quiet)
    run('chgrp {} {}'.format(group, remote_path), quiet=env.quiet)

    if owner is not None:
        run('chown {} {}'.format(owner, remote_path), quiet=env.quiet)

    if mode is not None:
        if isinstance(mode, int):
            run('chmod {:o} {}'.format(mode, remote_path), quiet=env.quiet)
        else:
            run('chmod {} {}'.format(mode, remote_path), quiet=env.quiet)


def is_dir(remote_path):
    """
    Check if the remote path is a directory
    """
    out = run('stat -L --format=%F {}'.format(remote_path), quiet=env.quiet)
    if out.succeeded and out == 'directory':
        return True
    return False
