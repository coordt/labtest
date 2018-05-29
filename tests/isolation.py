import os
import sys
import contextlib


PY2 = sys.version_info[0] == 2

if PY2:
    from cStringIO import StringIO
    iteritems = lambda x: x.iteritems()  # NOQA
else:
    import io
    iteritems = lambda x: iter(x.items())  # NOQA


def _is_binary_reader(stream, default=False):
    try:
        return isinstance(stream.read(0), bytes)
    except Exception:
        return default
        # This happens in some cases where the stream was already
        # closed.  In this case, we assume the default.


def _find_binary_reader(stream):
    # We need to figure out if the given stream is already binary.
    # This can happen because the official docs recommend detaching
    # the streams to get binary streams.  Some code might do this, so
    # we need to deal with this case explicitly.
    if _is_binary_reader(stream, False):
        return stream

    buf = getattr(stream, 'buffer', None)

    # Same situation here; this time we assume that the buffer is
    # actually binary in case it's closed.
    if buf is not None and _is_binary_reader(buf, True):
        return buf


def make_env(self, overrides=None):
    """Returns the environment overrides for invoking a script."""
    rv = {}
    if overrides:
        rv.update(overrides)
    return rv


@contextlib.contextmanager
def isolation(input=None, env=None, color=False):
    """A context manager that sets up the isolation for invoking of a
    command line tool.  This sets up stdin with the given input data
    and `os.environ` with the overrides from the given dictionary.
    This also rebinds some internals in Click to be mocked (like the
    prompt functionality).

    This is automatically done in the :meth:`invoke` method.

    .. versionadded:: 4.0
       The ``color`` parameter was added.

    :param input: the input stream to put into sys.stdin.
    :param env: the environment overrides as dictionary.
    :param color: whether the output should contain color codes. The
                  application can still override this explicitly.
    """
    charset = 'utf-8'
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    env = make_env(env)

    if PY2:
        sys.stdout = bytes_output = StringIO()
        sys.stderr = bytes_err_output = StringIO()
    else:
        bytes_output = io.BytesIO()
        bytes_err_output = io.BytesIO()
        sys.stdout = io.TextIOWrapper(bytes_output, encoding=charset)
        sys.stderr = io.TextIOWrapper(bytes_err_output, encoding=charset)

    def visible_input(prompt=None):
        sys.stdout.write(prompt or '')
        val = input.readline().rstrip('\r\n')
        sys.stdout.write(val + '\n')
        sys.stdout.flush()
        return val

    def hidden_input(prompt=None):
        sys.stdout.write((prompt or '') + '\n')
        sys.stdout.flush()
        return input.readline().rstrip('\r\n')

    def _getchar(echo):
        char = sys.stdin.read(1)
        if echo:
            sys.stdout.write(char)
            sys.stdout.flush()
        return char

    default_color = color

    def should_strip_ansi(stream=None, color=None):
        if color is None:
            return not default_color
        return not color

    old_env = {}
    try:
        for key, value in iteritems(env):
            old_env[key] = os.environ.get(key)
            if value is None:
                try:
                    del os.environ[key]
                except Exception:
                    pass
            else:
                os.environ[key] = value
        yield bytes_output, bytes_err_output
    finally:
        for key, value in iteritems(old_env):
            if value is None:
                try:
                    del os.environ[key]
                except Exception:
                    pass
            else:
                os.environ[key] = value
        sys.stdout = old_stdout
        sys.stderr = old_stderr
