import pytest
import click
from .fabric_runner import run_fabric_command
from labtest import services


def test_start_service():
    responses = {
        '/bin/bash -l -c "systemctl is-active testing-testinstance"': 'inactive',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl start testing-testinstance"': '',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: systemctl is-active testing-testinstance\n'
        '[{host}] out: inactive\n'
        '[{host}] sudo: systemctl start testing-testinstance\n'
    )
    run_fabric_command(services.start_service, responses, expected, files, env, None, 'testing-testinstance')


def test_start_service_active():
    responses = {
        '/bin/bash -l -c "systemctl is-active testing-testinstance"': 'active',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: systemctl is-active testing-testinstance\n'
        '[{host}] out: active\n'
    )
    run_fabric_command(services.start_service, responses, expected, files, env, None, 'testing-testinstance')


def test_start_service_unknown():
    responses = {
        '/bin/bash -l -c "systemctl is-active testing-testinstance"': 'unknown',
    }
    env = {}
    files = {}
    expected = (
        '[{host}] run: systemctl is-active testing-testinstance\n'
        '[{host}] out: unknown\n'
    )
    with pytest.raises(click.ClickException):
        run_fabric_command(services.start_service, responses, expected, files, env, None, 'testing-testinstance')


def test_delete_service():
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /etc/systemd/system/testing-testinstance.service)\\""': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl stop testing-testinstance.service"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl disable testing-testinstance.service"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "rm /etc/systemd/system/testing-testinstance.service"': '',
    }
    env = {}
    files = {
        '/etc/systemd/system/testing-testinstance.service': 'asdf',
    }
    expected = (
        'Deleting the OS service: testing-testinstance\n'
        '[{host}] sudo: systemctl stop testing-testinstance.service\n'
        '[{host}] sudo: systemctl disable testing-testinstance.service\n'
        '[{host}] sudo: rm /etc/systemd/system/testing-testinstance.service\n'
    )
    run_fabric_command(services.delete_service, responses, expected, files, env, None, 'testing-testinstance')


def test_setup_service():
    import os

    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "systemctl is-active testing-testinstance"': 'active',
        '/bin/bash -l -c "test -d \\"\\$(echo /tmp/testing-testinstance.service)\\""': '',
        '/bin/bash -l -c "stat \\"\\$(echo /tmp/testing-testinstance.service/systemd-test.conf.template)\\""': ('', 'no exist', 1),
        '/bin/bash -l -c "stat \\"\\$(echo /etc/systemd/system/testing-testinstance.service)\\""': ('', 'no exist', 1),
        '/bin/bash -l -c "stat \\"\\$(echo /tmp/testing-testinstance.service)\\""': ('', 'no exist', 1),
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "mv /tmp/testing-testinstance.service /etc/systemd/system/testing-testinstance.service"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl enable testing-testinstance.service"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl start testing-testinstance.service"': '',
    }
    env = {}
    files = {
        '/tmp/testing-testinstance.service': '',
    }
    expected = (
        'Creating the OS service.\n'
        'No Such File: /tmp/testing-testinstance.service/systemd-test.conf.template\n'
        '[{host}] sudo: mv /tmp/testing-testinstance.service /etc/systemd/system/testing-testinstance.service\n'
        '[{host}] sudo: systemctl enable testing-testinstance.service\n'
        'Starting the OS service: testing-testinstance\n'
        '[{host}] sudo: systemctl start testing-testinstance.service\n'
    )
    local_template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../labtest/templates/systemd-test.conf.template'))
    context = {}
    run_fabric_command(services.setup_service, responses, expected, files, env, None, 'testing-testinstance', local_template_path, context)


def test_setup_service_exists():
    import os

    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /etc/systemd/system/testing-testinstance.service)\\""': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl start testing-testinstance.service"': '',
        '/bin/bash -l -c "systemctl is-active testing-testinstance"': 'active',
    }
    env = {}
    files = {
        '/tmp/testing-testinstance.service': '',
    }
    expected = (
        '[{host}] run: systemctl is-active testing-testinstance\n'
        '[{host}] out: active\n'
    )
    local_template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../labtest/templates/systemd-test.conf.template'))
    context = {}
    run_fabric_command(services.setup_service, responses, expected, files, env, None, 'testing-testinstance', local_template_path, context)
