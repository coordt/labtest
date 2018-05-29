from .fabric_runner import run_fabric_command
from labtest import filesystem


def test_get_file_contents():
    responses = {
    }
    env = {}
    files = {
        '/testing/testfile': 'foobar',
    }
    expected = ''
    response = run_fabric_command(filesystem.get_file_contents, responses, expected, files, env, None, '/testing/testfile')
    assert response.getvalue() == 'foobar'


def test_create_dir():
    responses = {
        '/bin/bash -l -c "mkdir -p /testing/testdir"': '',
        '/bin/bash -l -c "chgrp docker /testing/testdir"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: mkdir -p /testing/testdir\n'
        '[{host}] run: chgrp docker /testing/testdir\n'
    )
    run_fabric_command(filesystem.create_dir, responses, expected, files, env, None, '/testing/testdir')


def test_create_dir_owner():
    responses = {
        '/bin/bash -l -c "mkdir -p /testing/testdir"': '',
        '/bin/bash -l -c "chgrp docker /testing/testdir"': '',
        '/bin/bash -l -c "chown foo /testing/testdir"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: mkdir -p /testing/testdir\n'
        '[{host}] run: chgrp docker /testing/testdir\n'
        '[{host}] run: chown foo /testing/testdir\n'
    )
    run_fabric_command(filesystem.create_dir, responses, expected, files, env, None, '/testing/testdir', owner='foo')


def test_create_dir_group():
    responses = {
        '/bin/bash -l -c "mkdir -p /testing/testdir"': '',
        '/bin/bash -l -c "chgrp foo /testing/testdir"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: mkdir -p /testing/testdir\n'
        '[{host}] run: chgrp foo /testing/testdir\n'
    )
    run_fabric_command(filesystem.create_dir, responses, expected, files, env, None, '/testing/testdir', group='foo')


def test_create_dir_mode():
    responses = {
        '/bin/bash -l -c "mkdir -p /testing/testdir"': '',
        '/bin/bash -l -c "chgrp docker /testing/testdir"': '',
        '/bin/bash -l -c "chmod 755 /testing/testdir"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: mkdir -p /testing/testdir\n'
        '[{host}] run: chgrp docker /testing/testdir\n'
        '[{host}] run: chmod 755 /testing/testdir\n'
    )
    run_fabric_command(filesystem.create_dir, responses, expected, files, env, None, '/testing/testdir', mode='755')
    run_fabric_command(filesystem.create_dir, responses, expected, files, env, None, '/testing/testdir', mode=493)


def test_is_dir():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /testing/testdir"': 'directory',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /testing/testdir\n'
        '[{host}] out: directory\n'
    )
    response = run_fabric_command(filesystem.is_dir, responses, expected, files, env, None, '/testing/testdir')
    assert response

    responses = {
        '/bin/bash -l -c "stat -L --format=%F /testing/testdir"': 'regular file',
    }
    expected = (
        '[{host}] run: stat -L --format=%F /testing/testdir\n'
        '[{host}] out: regular file\n'
    )
    response = run_fabric_command(filesystem.is_dir, responses, expected, files, env, None, '/testing/testdir')
    assert not response
