from fabric.api import env
from .mock_sshserver import Server, HOST, PORT, USER, CLIENT_PRIVKEY
from .fake_filesystem import FakeFilesystem
from .isolation import isolation
from labtest import instance


class FabricException(Exception):
    pass


def setup_config(port=PORT, **kwargs):
    from labtest.config import get_config
    cfg = get_config(
        host='127.0.0.1',
        app_name='testapp',
        code_repo_url='git@github.com:example/example.git',
        build_provider='default'
    )
    instance._setup_env_with_config(cfg)
    if 'branch_name' in kwargs:
        instance._setup_default_env('testinstance', kwargs['branch_name'])
    else:
        if 'branch_name' in env:
            del env['branch_name']
        instance._setup_default_env('testinstance')
    env.hosts = ['{}@{}:{}'.format(USER, HOST, port), ]
    env.quiet = False
    env.host_string = env.hosts[0]
    env.key_filename = CLIENT_PRIVKEY
    env.abort_exception = FabricException
    env.test_domain = 'test.example.com'
    env.container_build_command = cfg.container_build_command
    env.update(kwargs)
    return cfg


def run_fabric_command(command, responses, expected, files=None, environ=None, port=None, *args, **kwargs):
    """
    Does the actual running of the command and testing the output
    """
    import random

    if port is None:
        port = random.randint(1024, 49151)

    if environ is not None:
        setup_config(port=port, **environ)
    else:
        setup_config(port=port)

    users = {USER: CLIENT_PRIVKEY, }

    if files is not None:
        ffs = FakeFilesystem(files)
    else:
        ffs = FakeFilesystem({})
    exception = False
    expected = expected.format(host=env.host_string)

    with isolation() as out:
        with Server(users=users, port=port, responses=responses, files=ffs):
            try:
                response = command(*args, **kwargs)
            except FabricException as e:
                exception = True

    output = out[0].getvalue()
    error = out[1].getvalue()

    if output != expected or exception:
        print ''
        print "STDOUT:", output
    if error or exception:
        print ''
        print "STDERR:", error
    if exception:
        raise e
    else:
        assert output == expected
    return response
