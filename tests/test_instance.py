#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_labtest
----------------------------------

Tests for `labtest instance` module.
"""

from click.testing import CliRunner
from fabric.api import env
from labtest import instance
from labtest import cli
from .fabric_runner import setup_config, run_fabric_command


def run_fabric_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output


def test_default_env():
    """
    Make sure all the correct stuff is added to the default env
    """
    cfg = setup_config(branch_name='testbranch')
    assert env.instance_name == 'testinstance'
    assert env.app_path == '/testing/testapp'
    assert env.instance_path == '/testing/testapp/testinstance'
    assert env.service_name == 'testapp-testinstance'
    assert env.network_name == 'testapp-testinstance-net'
    assert env.context == {
        'APP_NAME': 'testapp',
        'INSTANCE_NAME': 'testinstance',
        'BRANCH_NAME': 'testbranch',
    }
    assert env.docker_image == cfg.docker_image_pattern % {
        'APP_NAME': 'testapp',
        'INSTANCE_NAME': 'testinstance',
    }


def test_git_cmd():
    responses = {
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "git status"': ''
    }
    expected = '[{host}] sudo: git status\n'
    run_fabric_command(instance._git_cmd, responses, expected, None, None, None, 'git status')


def test_virtual_host_name():
    assert instance._virtual_host_name() == 'testapp-testinstance.test.example.com'


def test_remove_path():
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance)\\""': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "rm -Rf /testing/testapp/testinstance"': '',
    }
    expected = (
        "Checking for code path: /testing/testapp/testinstance\n"
        "  Found. Removing...\n"
        "[{host}] sudo: rm -Rf /testing/testapp/testinstance\n"
    )
    run_fabric_command(instance._remove_path, responses, expected)


def test_setup_path():
    responses = {
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "mkdir -p /testing/testapp/testinstance"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "chgrp -R docker /testing"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "chmod -R g+w /testing"': '',
    }
    expected = (
        '[{host}] sudo: mkdir -p /testing/testapp/testinstance\n'
        '[{host}] sudo: chgrp -R docker /testing\n'
        '[{host}] sudo: chmod -R g+w /testing\n'
    )
    run_fabric_command(instance._setup_path, responses, expected)


def test_checkout_code_first_time():
    responses = {
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance >/dev/null && chgrp -R docker /testing/testapp/testinstance; chmod -R g+w /testing/testapp/testinstance"': '',
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance >/dev/null && git clone git@github.com:example/example.git code --branch testbranch --depth 1"': '',
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance/code >/dev/null && chgrp -R docker /testing/testapp/testinstance; chmod -R g+w /testing/testapp/testinstance"': '',
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/code)\\""': ('', 'fail', 1),
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance/code >/dev/null && git rev-parse --verify HEAD"': 'testbranch',
    }
    expected = (
        'Checking out code from: git@github.com:example/example.git\n'
        '[{host}] sudo: git clone git@github.com:example/example.git code --branch testbranch --depth 1\n'
        '[{host}] sudo: chgrp -R docker /testing/testapp/testinstance; chmod -R g+w /testing/testapp/testinstance\n'
        '[{host}] sudo: git rev-parse --verify HEAD\n'
        '[{host}] out: testbranch\n'
    )
    run_fabric_command(instance._checkout_code, responses, expected, environ={'branch_name': 'testbranch'})


def test_checkout_code_second_time():
    responses = {
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance >/dev/null && chgrp -R docker /testing/testapp/testinstance; chmod -R g+w /testing/testapp/testinstance"': '',
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance/code >/dev/null && chgrp -R docker /testing/testapp/testinstance; chmod -R g+w /testing/testapp/testinstance"': '',
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance/code >/dev/null && git fetch --depth 1; git reset --hard origin/testbranch; git clean -dfx"': '',
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance/code >/dev/null && git rev-parse --verify HEAD"': 'testbranch',
        'sudo -S -p \'sudo password:\'  -u "ec2-user"  /bin/bash -l -c "cd /testing/testapp/testinstance/code >/dev/null && git rev-parse --abbrev-ref HEAD"': 'testbranch',
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/code)\\""': '',
    }
    expected = (
        'Fetching most recent code from: git@github.com:example/example.git\n'
        '[{host}] sudo: git rev-parse --abbrev-ref HEAD\n'
        '[{host}] out: testbranch\n'
        '[{host}] sudo: git fetch --depth 1; git reset --hard origin/testbranch; git clean -dfx\n'
        '[{host}] sudo: chgrp -R docker /testing/testapp/testinstance; chmod -R g+w /testing/testapp/testinstance\n'
        '[{host}] sudo: git rev-parse --verify HEAD\n'
        '[{host}] out: testbranch\n'
    )
    run_fabric_command(instance._checkout_code, responses, expected)


def test_app_build_empty():
    responses = {}
    expected = ''
    run_fabric_command(instance._app_build, responses, expected)


def test_app_build():
    responses = {
        '/bin/bash -l -c "docker run --rm -ti -v /testing/testapp/testinstance:/build -w /build node ./build_app"': '',
    }
    env = {
        'app_build_command': './build_app',
        'app_build_image': 'node',
    }
    expected = (
        'Building the application using node and ./build_app.\n'
        '[{host}] run: docker run --rm -ti -v /testing/testapp/testinstance:/build -w /build node ./build_app\n'
    )
    run_fabric_command(instance._app_build, responses, expected, None, env)


def test_image_build():
    responses = {
        '/bin/bash -l -c "cd /testing/testapp/testinstance >/dev/null && ./docker-build -a testapp -i testinstance"': '',
    }
    env = {}
    files = {
        '/testing/testapp/testinstance/docker-build': '',
    }
    expected = (
        'Building the Docker image.\n'
        '[{host}] run: ./docker-build -a testapp -i testinstance\n'
    )
    run_fabric_command(instance._image_build, responses, expected, files, env)


def test_setup_network():
    # Network doesn't exist
    responses = {
        '/bin/bash -l -c "docker network ls --filter name=testapp-testinstance-net --format \\"{{.ID}}\\""': '',
        '/bin/bash -l -c "docker network create --driver bridge testapp-testinstance-net"': '',
        '/bin/bash -l -c "docker network connect testapp-testinstance-net nginx_proxy"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: docker network ls --filter name=testapp-testinstance-net --format "{{{{.ID}}}}"\n'
        'Setting up networking.\n'
        '[{host}] run: docker network create --driver bridge testapp-testinstance-net\n'
        '[{host}] run: docker network connect testapp-testinstance-net nginx_proxy\n'
    )
    run_fabric_command(instance._setup_network, responses, expected, files, env)

    # Network exists
    responses = {
        '/bin/bash -l -c "docker network ls --filter name=testapp-testinstance-net --format \\"{{.ID}}\\""': '12345',
    }
    expected = (
        '[{host}] run: docker network ls --filter name=testapp-testinstance-net --format "{{{{.ID}}}}"\n'
        '[{host}] out: 12345\n'
    )
    run_fabric_command(instance._setup_network, responses, expected, files, env)


def test_delete_network():
    # Network doesn't exist
    responses = {
        '/bin/bash -l -c "docker network ls --filter name=testapp-testinstance-net --format \\"{{.ID}}\\""': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: docker network ls --filter name=testapp-testinstance-net --format "{{{{.ID}}}}"\n'
    )
    run_fabric_command(instance._delete_network, responses, expected, files, env)

    # Network exists
    responses = {
        '/bin/bash -l -c "docker network ls --filter name=testapp-testinstance-net --format \\"{{.ID}}\\""': '12345',
        '/bin/bash -l -c "docker network disconnect testapp-testinstance-net nginx_proxy"': '',
        '/bin/bash -l -c "docker network rm testapp-testinstance-net"': '',
    }
    expected = (
        '[{host}] run: docker network ls --filter name=testapp-testinstance-net --format "{{{{.ID}}}}"\n'
        '[{host}] out: 12345\n'
        'Removing network.\n'
        '[{host}] run: docker network disconnect testapp-testinstance-net nginx_proxy\n'
        '[{host}] run: docker network rm testapp-testinstance-net\n'
    )
    run_fabric_command(instance._delete_network, responses, expected, files, env)


def test_setup_templates():
    responses = {
        '/bin/bash -l -c "docker network ls --filter name=testapp-testinstance-net --format \\"{{.ID}}\\""': '',
    }
    env = {}
    files = {
        '/testing/testapp/testinstance/test.env': '',
    }
    expected = (
        'Writing the experiment\'s environment file.\n'
    )
    run_fabric_command(instance._setup_templates, responses, expected, files, env)


def test_update_container():
    responses = {
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance --filter ancestor=testapp/testinstance:latest --format \\"{{.ID}}\\""': '',
        '/bin/bash -l -c "docker create --env-file /testing/testapp/testinstance/test.env --name testapp-testinstance --network testapp-testinstance-net testapp/testinstance:latest"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: docker ps -a --filter name=testapp-testinstance --filter ancestor=testapp/testinstance:latest --format "{{{{.ID}}}}"\n'
        'Creating the Docker container.\n'
        '[{host}] run: docker create --env-file /testing/testapp/testinstance/test.env --name testapp-testinstance --network testapp-testinstance-net testapp/testinstance:latest\n'
    )
    run_fabric_command(instance._update_container, responses, expected, files, env)


def test_update_container_container_exists():
    responses = {
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance --filter ancestor=testapp/testinstance:latest --format \\"{{.ID}}\\""': '12345',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl stop testapp-testinstance"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl start testapp-testinstance"': '',
        '/bin/bash -l -c "docker create --env-file /testing/testapp/testinstance/test.env --name testapp-testinstance --network testapp-testinstance-net testapp/testinstance:latest"': '',
        '/bin/bash -l -c "docker rm -f testapp-testinstance"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: docker ps -a --filter name=testapp-testinstance --filter ancestor=testapp/testinstance:latest --format "{{{{.ID}}}}"\n'
        '[{host}] out: 12345\n'
        'Removing the existing container.\n'
        '[{host}] sudo: systemctl stop testapp-testinstance\n'
        '[{host}] run: docker rm -f testapp-testinstance\n'
        'Creating the Docker container.\n'
        '[{host}] run: docker create --env-file /testing/testapp/testinstance/test.env --name testapp-testinstance --network testapp-testinstance-net testapp/testinstance:latest\n'
        'Starting the new container.\n'
        '[{host}] sudo: systemctl start testapp-testinstance\n'
    )
    run_fabric_command(instance._update_container, responses, expected, files, env)
