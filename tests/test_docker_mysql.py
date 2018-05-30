#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from labtest.provider.docker import mysql
from .fabric_runner import run_fabric_command
import click
import pytest

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures'))


def test_get_initial_data_source_directory():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/"': 'directory',
        '/bin/bash -l -c "ls -1td /backups/testapp/* | head -1"': '/backups/testapp/db-backup-2018-05-29.sql.gz',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/\n'
        '[{host}] out: directory\n'
        '[{host}] run: ls -1td /backups/testapp/* | head -1\n'
        '[{host}] out: /backups/testapp/db-backup-2018-05-29.sql.gz\n'
    )
    run_fabric_command(mysql._get_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/')


def test_get_initial_data_source_file():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz"': 'regular file',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz\n'
        '[{host}] out: regular file\n'
    )
    run_fabric_command(mysql._get_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/db-backup-2018-05-29.sql.gz')


def test_get_initial_data_source_empty_dir():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/"': 'directory',
        '/bin/bash -l -c "ls -1td /backups/testapp/* | head -1"': ('', 'empty', 127),
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/\n'
        '[{host}] out: directory\n'
        '[{host}] run: ls -1td /backups/testapp/* | head -1\n'
        '[{host}] out: empty\n'
    )
    with pytest.raises(click.ClickException):
        run_fabric_command(mysql._get_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/')


def test_get_initial_data_source_strange():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/"': 'foo',
        '/bin/bash -l -c "ls -1td /backups/testapp/* | head -1"': ('', 'empty', 127),
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/\n'
        '[{host}] out: foo\n'
    )
    with pytest.raises(click.ClickException):
        run_fabric_command(mysql._get_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/')


def test_get_initial_data_source_missing():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/"': ('', 'No such file or directory', 1),
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/\n'
        '[{host}] out: No such file or directory\n'
    )
    with pytest.raises(click.ClickException):
        run_fabric_command(mysql._get_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/')


def test_setup_initial_data_source():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz"': 'regular file',
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/initialdata)\\""': ('', 'fail', 1),
        '/bin/bash -l -c "mkdir -p /testing/testapp/testinstance/initialdata"': '',
        '/bin/bash -l -c "chgrp docker /testing/testapp/testinstance/initialdata"': '',
        '/bin/bash -l -c "ln -s /backups/testapp/db-backup-2018-05-29.sql.gz /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz\n'
        '[{host}] out: regular file\n'
        '[{host}] run: mkdir -p /testing/testapp/testinstance/initialdata\n'
        '[{host}] run: chgrp docker /testing/testapp/testinstance/initialdata\n'
        '[{host}] run: ln -s /backups/testapp/db-backup-2018-05-29.sql.gz /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
        '  Created a symlink from /backups/testapp/db-backup-2018-05-29.sql.gz -> /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
    )
    run_fabric_command(mysql._setup_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/db-backup-2018-05-29.sql.gz')


def test_setup_initial_data_source_link_exists():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz"': 'regular file',
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/initialdata)\\""': '',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz)\\""': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz\n'
        '[{host}] out: regular file\n'
    )
    run_fabric_command(mysql._setup_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/db-backup-2018-05-29.sql.gz')


def test_setup_initial_data_source_link_old():
    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz"': 'regular file',
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/initialdata)\\""': '',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz)\\""': ('', 'fail', 1),
        '/bin/bash -l -c "rm -Rf /testing/testapp/testinstance/initialdata/*"': '',
        '/bin/bash -l -c "ln -s /backups/testapp/db-backup-2018-05-29.sql.gz /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {}
    expected = (
        '[{host}] run: stat -L --format=%F /backups/testapp/db-backup-2018-05-29.sql.gz\n'
        '[{host}] out: regular file\n'
        '[{host}] run: rm -Rf /testing/testapp/testinstance/initialdata/*\n'
        '[{host}] run: ln -s /backups/testapp/db-backup-2018-05-29.sql.gz /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
        '  Created a symlink from /backups/testapp/db-backup-2018-05-29.sql.gz -> /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
    )
    run_fabric_command(mysql._setup_initial_data_source, responses, expected, files, environ, None, '/backups/testapp/db-backup-2018-05-29.sql.gz')


def test_setup_env_file():
    responses = {
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = ''
    mysql_env = [
        "MYSQL_ALLOW_EMPTY_PASSWORD=true",
        "MYSQL_DATABASE=drupal",
    ]
    run_fabric_command(mysql._setup_env_file, responses, expected, files, environ, None, '/testing/testapp/testinstance/testapp-testinstance-db.env', mysql_env)


def test_get_service_config():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    assert svc_config['app_name'] == 'testapp'
    assert svc_config['name'] == 'db'
    assert svc_config['initial_data_source'] == '/backups/testapp/'
    assert svc_config['image'] == 'mysql:5.6'
    assert svc_config['commands'] == [
        "--character-set-server=utf8mb4",
        "--collation-server=utf8mb4_unicode_ci",
    ]
    assert svc_config['environment'] == [
        "MYSQL_ALLOW_EMPTY_PASSWORD=true",
        "MYSQL_DATABASE=drupal",
    ]


def test_setup_volume():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "docker volume ls --filter name=testapp-testinstance-db-data -q"': '',
        '/bin/bash -l -c "docker volume create --driver rexray/ebs:latest --opt=size=10 testapp-testinstance-db-data"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
    }
    expected = (
        '[{host}] run: docker volume ls --filter name=testapp-testinstance-db-data -q\n'
        '  Creating a volume for storing MySQL data.\n'
        '[{host}] run: docker volume create --driver rexray/ebs:latest --opt=size=10 testapp-testinstance-db-data\n'
    )
    run_fabric_command(mysql._setup_volume, responses, expected, files, environ, None, svc_config)


def test_setup_volume_exists():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "docker volume ls --filter name=testapp-testinstance-db-data -q"': 'testapp-testinstance-mysql-data',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
    }
    expected = (
        '[{host}] run: docker volume ls --filter name=testapp-testinstance-db-data -q\n'
        '[{host}] out: testapp-testinstance-mysql-data\n'
    )
    run_fabric_command(mysql._setup_volume, responses, expected, files, environ, None, svc_config)


def test_delete_volume():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "docker volume ls --filter name=testapp-testinstance-db-data -q"': 'testapp-testinstance-db-data',
        '/bin/bash -l -c "docker volume rm testapp-testinstance-db-data"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
    }
    expected = (
        '[{host}] run: docker volume ls --filter name=testapp-testinstance-db-data -q\n'
        '[{host}] out: testapp-testinstance-db-data\n'
        '  Deleting volume testapp-testinstance-db-data.\n'
        '[{host}] run: docker volume rm testapp-testinstance-db-data\n'
    )
    run_fabric_command(mysql._delete_volume, responses, expected, files, environ, None, svc_config)


def test_delete_volume_no_volume():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "docker volume ls --filter name=testapp-testinstance-db-data -q"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
    }
    expected = (
        '[{host}] run: docker volume ls --filter name=testapp-testinstance-db-data -q\n'
    )
    run_fabric_command(mysql._delete_volume, responses, expected, files, environ, None, svc_config)


def test_setup_container():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    svc_config['initial_data_source'] = '/testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz'
    responses = {
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance-db --format \\"{{.ID}}\\""': '',
        '/bin/bash -l -c "docker create --name testapp-testinstance-db --network testapp-testinstance-net --net-alias db -v testapp-testinstance-db-data:/var/lib/mysql --env-file /testing/testapp/testinstance/testapp-testinstance-db.env -v /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz:/docker-entrypoint-initdb.d/db-backup-2018-05-29.sql.gz mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = (
        '  Setting up the testapp-testinstance-db container\n'
        '[{host}] run: docker ps -a --filter name=testapp-testinstance-db --format "{{{{.ID}}}}"\n'
        '[{host}] run: docker create --name testapp-testinstance-db --network testapp-testinstance-net --net-alias db -v testapp-testinstance-db-data:/var/lib/mysql --env-file /testing/testapp/testinstance/testapp-testinstance-db.env -v /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz:/docker-entrypoint-initdb.d/db-backup-2018-05-29.sql.gz mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci\n'
    )
    run_fabric_command(mysql._setup_container, responses, expected, files, environ, None, svc_config)


def test_setup_container_existing():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    svc_config['initial_data_source'] = '/testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz'
    responses = {
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance-db --format \\"{{.ID}}\\""': '12345',
        '/bin/bash -l -c "docker create --name testapp-testinstance-db --network testapp-testinstance-net --net-alias db -v testapp-testinstance-db-data:/var/lib/mysql --env-file /testing/testapp/testinstance/testapp-testinstance-db.env -v /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz:/docker-entrypoint-initdb.d/db-backup-2018-05-29.sql.gz mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl stop testapp-testinstance-db"': '',
        '/bin/bash -l -c "docker rm -f testapp-testinstance-db"': '',
        '/bin/bash -l -c "docker volume prune -f"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl start testapp-testinstance-db"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = (
        '  Setting up the testapp-testinstance-db container\n'
        '[{host}] run: docker ps -a --filter name=testapp-testinstance-db --format "{{{{.ID}}}}"\n'
        '[{host}] out: 12345\n'
        '  Removing existing container.\n'
        '[{host}] sudo: systemctl stop testapp-testinstance-db\n'
        '[{host}] run: docker rm -f testapp-testinstance-db\n'
        '[{host}] run: docker volume prune -f\n'
        '[{host}] run: docker create --name testapp-testinstance-db --network testapp-testinstance-net --net-alias db -v testapp-testinstance-db-data:/var/lib/mysql --env-file /testing/testapp/testinstance/testapp-testinstance-db.env -v /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz:/docker-entrypoint-initdb.d/db-backup-2018-05-29.sql.gz mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci\n'
        '  Starting new container.\n'
        '[{host}] sudo: systemctl start testapp-testinstance-db\n'
    )
    run_fabric_command(mysql._setup_container, responses, expected, files, environ, None, svc_config)


def test_delete_container():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance-db --format \\"{{.ID}}\\""': '12345',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl stop testapp-testinstance-db"': '',
        '/bin/bash -l -c "docker rm -f testapp-testinstance-db"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = (
        '[{host}] run: docker ps -a --filter name=testapp-testinstance-db --format "{{{{.ID}}}}"\n'
        '[{host}] out: 12345\n'
        '  Deleting the testapp-testinstance-db container\n'
        '[{host}] sudo: systemctl stop testapp-testinstance-db\n'
        '[{host}] run: docker rm -f testapp-testinstance-db\n'
    )
    run_fabric_command(mysql._delete_container, responses, expected, files, environ, None, svc_config)


def test_delete_container_none():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance-db --format \\"{{.ID}}\\""': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = (
        '[{host}] run: docker ps -a --filter name=testapp-testinstance-db --format "{{{{.ID}}}}"\n'
    )
    run_fabric_command(mysql._delete_container, responses, expected, files, environ, None, svc_config)


def test_write_config():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = ''
    run_fabric_command(mysql._write_config, responses, expected, files, environ, None, svc_config, '/testing/testapp/testinstance/testapp-testinstance-db.env')


def test_delete_config():
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.env)\\""': 'regular file',
        '/bin/bash -l -c "rm /testing/testapp/testinstance/testapp-testinstance-db.env"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = '[{host}] run: rm /testing/testapp/testinstance/testapp-testinstance-db.env\n'
    run_fabric_command(mysql._delete_config, responses, expected, files, environ, None, '/testing/testapp/testinstance/testapp-testinstance-db.env')


def test_delete_config_none():
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.env)\\""': ('', 'no exist', 1),
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
    }
    expected = ''
    run_fabric_command(mysql._delete_config, responses, expected, files, environ, None, '/testing/testapp/testinstance/testapp-testinstance-db.env')


def test_has_config_changed_unchanged():
    import json
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.conf.json)\\""': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.conf.json': json.dumps(svc_config),
    }
    expected = '  Configuration for existing MySQL service is unchanged. Skipping.\n'
    response = run_fabric_command(mysql._has_config_changed, responses, expected, files, environ, None, svc_config)
    assert response is False


def test_has_config_changed_changed():
    import json
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.conf.json)\\""': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.conf.json': json.dumps(svc_config),
    }
    svc_config['environment'].append('FOO=bar')
    expected = (
        '  Configuration for existing MySQL service has changed.\n'
        '    environment was [u\'MYSQL_ALLOW_EMPTY_PASSWORD=true\', u\'MYSQL_DATABASE=drupal\'] now [\'MYSQL_ALLOW_EMPTY_PASSWORD=true\', \'MYSQL_DATABASE=drupal\', \'FOO=bar\']\n'
        '  Re-creating it.\n'
    )
    response = run_fabric_command(mysql._has_config_changed, responses, expected, files, environ, None, svc_config)
    assert response is True


def test_has_config_changed_change_options():
    import json
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.conf.json)\\""': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.conf.json': json.dumps(svc_config),
    }
    svc_config['foo'] = 'bar'
    expected = (
        '  Configuration for existing MySQL service has different options from the new configuration.\n'
        '    - foo\n'
        '  Re-creating it.\n'
    )
    response = run_fabric_command(mysql._has_config_changed, responses, expected, files, environ, None, svc_config)
    assert response is True


def test_has_config_changed_bad_file():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.conf.json)\\""': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.conf.json': '',
    }
    expected = (
        '  Error: No JSON object could be decoded\n'
        '  Configuration for existing MySQL service is unreadable. Re-creating it.\n'
    )
    response = run_fabric_command(mysql._has_config_changed, responses, expected, files, environ, None, svc_config)
    assert response is True


def test_has_config_changed_missing():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))
    svc_config = mysql._get_service_config(cfg.services['db'], 'db')
    responses = {
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.conf.json)\\""': ('', 'no exist', 1),
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.conf.json': '',
    }
    expected = ''
    response = run_fabric_command(mysql._has_config_changed, responses, expected, files, environ, None, svc_config)
    assert response is True


def test_create():
    from .fabric_runner import setup_config
    cfg = setup_config(filepath=os.path.join(FIXTURE_DIR, 'mysql-config.yml'))

    responses = {
        '/bin/bash -l -c "stat -L --format=%F /backups/testapp/"': 'directory',
        '/bin/bash -l -c "ls -1td /backups/testapp/* | head -1"': '/backups/testapp/db-backup-2018-05-29.sql.gz',
        '/bin/bash -l -c "echo \\"Will you echo quotation marks\\""': 'Will you echo quotation marks',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/initialdata)\\""': ('', 'fail', 1),
        '/bin/bash -l -c "mkdir -p /testing/testapp/testinstance/initialdata"': '',
        '/bin/bash -l -c "chgrp docker /testing/testapp/testinstance/initialdata"': '',
        '/bin/bash -l -c "ln -s /backups/testapp/db-backup-2018-05-29.sql.gz /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz"': '',
        '/bin/bash -l -c "stat \\"\\$(echo /testing/testapp/testinstance/testapp-testinstance-db.conf.json)\\""': ('', 'fail', 1),
        '/bin/bash -l -c "docker pull mysql:5.6"': '',
        '/bin/bash -l -c "docker volume ls --filter name=testapp-testinstance-db-data -q"': '',
        '/bin/bash -l -c "docker volume create --driver rexray/ebs:latest --opt=size=10 testapp-testinstance-db-data"': '',
        '/bin/bash -l -c "docker ps -a --filter name=testapp-testinstance-db --format \\"{{.ID}}\\""': '',
        '/bin/bash -l -c "docker create --name testapp-testinstance-db --network testapp-testinstance-net --net-alias db -v testapp-testinstance-db-data:/var/lib/mysql --env-file /testing/testapp/testinstance/testapp-testinstance-db.env -v /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz:/docker-entrypoint-initdb.d/db-backup-2018-05-29.sql.gz mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci"': '',
        '/bin/bash -l -c "stat \\"\\$(echo /etc/systemd/system/testapp-testinstance-db.service)\\""': ('', 'fail', 1),
        '/bin/bash -l -c "test -d \\"\\$(echo /tmp/testapp-testinstance-db.service)\\""': '',
        '/bin/bash -l -c "stat \\"\\$(echo /tmp/testapp-testinstance-db.service)\\""': ('', 'fail', 1),
        '/bin/bash -l -c "stat \\"\\$(echo /tmp/testapp-testinstance-db.service/systemd-backing.conf.template)\\""': ('', 'no exist', 1),
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "mv /tmp/testapp-testinstance-db.service /etc/systemd/system/testapp-testinstance-db.service"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl enable testapp-testinstance-db.service"': '',
        'sudo -S -p \'sudo password:\'  /bin/bash -l -c "systemctl start testapp-testinstance-db.service"': '',
    }
    environ = {
        'filepath': os.path.join(FIXTURE_DIR, 'mysql-config.yml')
    }
    files = {
        '/testing/testapp/testinstance/testapp-testinstance-db.env': '',
        '/etc/systemd/system/testapp-testinstance-db.service': '',
        '/tmp/testapp-testinstance-db.service': '',
        '/tmp/testapp-testinstance-db.service/systemd-backing.conf.template': '',
        '/testing/testapp/testinstance/testapp-testinstance-db.conf.json': '',
    }
    expected = (
        'Creating MySQL service.\n'
        '  Getting the initial data source.\n'
        '[{host}] run: stat -L --format=%F /backups/testapp/\n'
        '[{host}] out: directory\n'
        '[{host}] run: ls -1td /backups/testapp/* | head -1\n'
        '[{host}] out: /backups/testapp/db-backup-2018-05-29.sql.gz\n'
        '[{host}] run: mkdir -p /testing/testapp/testinstance/initialdata\n'
        '[{host}] run: chgrp docker /testing/testapp/testinstance/initialdata\n'
        '[{host}] run: ln -s /backups/testapp/db-backup-2018-05-29.sql.gz /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
        '  Created a symlink from /backups/testapp/db-backup-2018-05-29.sql.gz -> /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
        '    Initial data source: /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz\n'
        '  Updating docker image "mysql:5.6" for backing service.\n'
        '[{host}] run: docker pull mysql:5.6\n'
        '[{host}] run: docker volume ls --filter name=testapp-testinstance-db-data -q\n'
        '  Creating a volume for storing MySQL data.\n'
        '[{host}] run: docker volume create --driver rexray/ebs:latest --opt=size=10 testapp-testinstance-db-data\n'
        '  Setting up the testapp-testinstance-db container\n'
        '[{host}] run: docker ps -a --filter name=testapp-testinstance-db --format "{{{{.ID}}}}"\n'
        '[{host}] run: docker create --name testapp-testinstance-db --network testapp-testinstance-net --net-alias db -v testapp-testinstance-db-data:/var/lib/mysql --env-file /testing/testapp/testinstance/testapp-testinstance-db.env -v /testing/testapp/testinstance/initialdata/db-backup-2018-05-29.sql.gz:/docker-entrypoint-initdb.d/db-backup-2018-05-29.sql.gz mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci\n'
        'Creating the OS service.\n'
        '[{host}] sudo: mv /tmp/testapp-testinstance-db.service /etc/systemd/system/testapp-testinstance-db.service\n'
        '[{host}] sudo: systemctl enable testapp-testinstance-db.service\n'
        'Starting the OS service: testapp-testinstance-db\n'
        '[{host}] sudo: systemctl start testapp-testinstance-db.service\n'
    )
    run_fabric_command(mysql.create, responses, expected, files, environ, None, cfg.services['db'], 'db')
