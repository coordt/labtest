import logging
import os
import select
import socket
import threading
import types
from fake_filesystem import FakeFilesystem
from mock_sftp import FakeSFTPServer

try:
    from queue import Queue
except ImportError:  # Python 2.7
    from Queue import Queue

import paramiko

logging.basicConfig(filename='testserver.log', level=logging.INFO)
logger = logging.getLogger('server.py')


def _local_file(filename):
    return os.path.join(os.path.dirname(__file__), filename)


SERVER_KEY_PATH = os.path.join(os.path.dirname(__file__), "server-key")
HOST = '127.0.0.1'
PORT = 2200
USER = 'username'
HOME = '/'
RESPONSES = {}
SERVER_PRIVKEY = _local_file('server_rsa_key.key')
CLIENT_PUBKEY = _local_file('client.key.pub')
CLIENT_PRIVKEY = _local_file('client.key')
FILES = FakeFilesystem({})


def _equalize(lists, fillval=None):
    """
    Pad all given list items in ``lists`` to be the same length.
    """
    lists = map(list, lists)
    upper = max(len(x) for x in lists)
    for lst in lists:
        diff = upper - len(lst)
        if diff:
            lst.extend([fillval] * diff)
    return lists


class Handler(paramiko.ServerInterface):

    log = logging.getLogger(__name__)

    def __init__(self, server, client_conn):
        self.server = server
        self.thread = None
        self.command_queues = {}
        client, _ = client_conn
        self.transport = t = paramiko.Transport(client)
        t.add_server_key(paramiko.RSAKey(filename=SERVER_PRIVKEY))
        t.set_subsystem_handler("sftp", paramiko.SFTPServer, sftp_si=FakeSFTPServer)

    def run(self):
        self.transport.start_server(server=self)
        while True:
            channel = self.transport.accept()
            if channel is None:
                break
            if channel.chanid not in self.command_queues:
                self.command_queues[channel.chanid] = Queue()
            t = threading.Thread(target=self.handle_client, args=(channel,))
            t.setDaemon(True)
            t.start()

    def handle_client(self, channel):
        try:
            command = self.command_queues[channel.chanid].get(block=True)
            self.log.debug("Executing %s", command)
            if command in self.server._responses:
                stdout, stderr, returncode = self.response(command)
            else:
                print "Unrecognized command:", command
                stderr = "Sorry, I don't recognize that command.\n"
                stdout = ''
                returncode = 1
            self.log.debug("This is stdout {}".format(stdout))
            channel.sendall(stdout)
            channel.sendall_stderr(stderr)
            channel.send_exit_status(returncode)
        except Exception:
            self.log.error("Error handling client (channel: %s)", channel, exc_info=True)
        finally:
            self.log.debug("handle_client finally")
            channel.close()

    def response(self, command):
        result = self.server._responses[command]
        stderr = ""
        status = 0
        self.log.debug('response result {} ({})'.format(result, type(result)))
        if isinstance(result, types.StringTypes):
            stdout = result
        else:
            size = len(result)
            if size == 1:
                stdout = result[0]
            elif size == 2:
                stdout, stderr = result
            elif size == 3:
                stdout, stderr, status = result
        # stdout, stderr = _equalize((stdout, stderr))
        self.log.debug('stdout: {}, stderr: {}'.format(stdout, stderr))
        return stdout, stderr, status

    def check_auth_publickey(self, username, key):
        try:
            _, known_public_key = self.server._users[username]
        except KeyError:
            self.log.debug("Unknown user '%s'", username)
            return paramiko.AUTH_FAILED
        if known_public_key == key:
            self.log.debug("Accepting public key for user '%s'", username)
            return paramiko.AUTH_SUCCESSFUL
        self.log.debug("Rejecting public ley for user '%s'", username)
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        self.log.debug("check_channel_exec_request '%s' '%s'", channel, command)
        self.command_queues.setdefault(channel.get_id(), Queue()).put(command)
        return True

    def check_channel_pty_request(self, *args):
        self.log.debug('check_channel_pty_request')
        return True

    def check_channel_shell_request(self, channel):
        self.log.debug('check_channel_pty_request')
        # self.event.set()
        return True

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "publickey"


class Server(object):

    host = HOST
    log = logger

    def __init__(self, users, port=PORT, responses=RESPONSES, files=FILES, pubkeys=False):
        self._socket = None
        self._thread = None
        self._users = {}
        self._responses = responses
        self._files = files
        self._pubkeys = pubkeys
        self._port = port
        self._home = '/'

        for uid, private_key_path in users.items():
            self.add_user(uid, private_key_path)

    def add_user(self, uid, private_key_path):
        k = paramiko.RSAKey.from_private_key_file(private_key_path)
        self._users[uid] = (private_key_path, k)

    def __enter__(self):
        self.log.debug('Entering context.')
        self._socket = s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self._port))
        s.listen(5)
        self._thread = t = threading.Thread(target=self._run)
        t.setDaemon(True)
        t.start()
        return self

    def _run(self):
        sock = self._socket
        while sock.fileno() > 0:
            self.log.debug("Waiting for incoming connections ...")
            rlist, _, _ = select.select([sock], [], [], 1.0)
            if rlist:
                conn, addr = sock.accept()
                self.log.debug("... got connection %s from %s", conn, addr)
                handler = Handler(self, (conn, addr))
                t = threading.Thread(target=handler.run)
                t.setDaemon(True)
                t.start()

    def __exit__(self, *exc_info):
        self.log.debug('Exiting context.')
        try:
            # self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.shutdown(socket.SHUT_WR)
            self._socket.close()
        except Exception as e:
            self.log.error('Got an error while exiting: {}'.format(e))
            # pass
        self._socket = None
        self._thread = None

    def client(self, uid):
        private_key_path, _ = self._users[uid]
        c = paramiko.SSHClient()
        host_keys = c.get_host_keys()
        key = paramiko.RSAKey.from_private_key_file(SERVER_KEY_PATH)
        host_keys.add(self.host, "ssh-rsa", key)
        host_keys.add("[%s]:%d" % (self.host, self.port), "ssh-rsa", key)
        c.set_missing_host_key_policy(paramiko.RejectPolicy())
        c.connect(hostname=self.host,
                  port=self.port,
                  username=uid,
                  key_filename=private_key_path,
                  allow_agent=False,
                  look_for_keys=False)
        return c

    @property
    def port(self):
        return self._socket.getsockname()[1]

    @property
    def users(self):
        return self._users.keys()
