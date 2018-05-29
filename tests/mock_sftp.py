# -*- coding: utf-8 -*-

import logging
import os
import paramiko
from fake_filesystem import FakeFile


logging.basicConfig(filename='testserver.log', level=logging.DEBUG)
logger = logging.getLogger('server.py')


class PrependList(list):
    def prepend(self, val):
        self.insert(0, val)


def expand(path):
    """
    '/foo/bar/biz' => ('/', 'foo', 'bar', 'biz')
    'relative/path' => ('relative', 'path')
    """
    # Base case
    if path in ['', os.path.sep]:
        return [path]
    ret = PrependList()
    directory, filename = os.path.split(path)
    while directory and directory != os.path.sep:
        ret.prepend(filename)
        directory, filename = os.path.split(directory)
    ret.prepend(filename)
    # Handle absolute vs relative paths
    ret.prepend(directory if directory == os.path.sep else '')
    return ret


def contains(folder, path):
    """
    contains(('a', 'b', 'c'), ('a', 'b')) => True
    contains('a', 'b', 'c'), ('f',)) => False
    """
    return False if len(path) >= len(folder) else folder[:len(path)] == path


def missing_folders(paths):
    """
    missing_folders(['a/b/c']) => ['a', 'a/b', 'a/b/c']
    """
    ret = []
    pool = set(paths)
    for path in paths:
        expanded = expand(path)
        for i in range(len(expanded)):
            folder = os.path.join(*expanded[:len(expanded) - i])
            if folder and folder not in pool:
                pool.add(folder)
                ret.append(folder)
    return ret


def canonicalize(path, home):
    ret = path
    if not os.path.isabs(path):
        ret = os.path.normpath(os.path.join(home, path))
    return ret


class FakeSFTPHandle(paramiko.SFTPHandle):
    """
    Extremely basic way to get SFTPHandle working with our fake setup.
    """
    def chattr(self, attr):
        self.readfile.attributes = attr
        return paramiko.SFTP_OK

    def stat(self):
        return self.readfile.attributes


class FakeSFTPServer(paramiko.SFTPServerInterface):
    def __init__(self, server, *args, **kwargs):
        self.server = server.server
        logger.debug('FakeSFTPServer __init__ server: {}'.format(server))
        files = self.server._files
        # Expand such that omitted, implied folders get added explicitly
        for folder in missing_folders(files.keys()):
            files[folder] = None
        self.files = files

    def canonicalize(self, path):
        """
        Make non-absolute paths relative to $HOME.
        """
        logger.debug('Canonicalize: {}'.format(path))
        return canonicalize(path, self.server._home)

    def list_folder(self, path):
        path = self.files.normalize(path)
        expanded_files = map(expand, self.files)
        expanded_path = expand(path)
        candidates = [x for x in expanded_files if contains(x, expanded_path)]
        children = []
        for candidate in candidates:
            cut = candidate[:len(expanded_path) + 1]
            if cut not in children:
                children.append(cut)
        results = [self.stat(os.path.join(*x)) for x in children]
        logger.debug('list_folder: {}'.format(results))
        bad = not results or any(x == paramiko.SFTP_NO_SUCH_FILE for x in results)
        return paramiko.SFTP_NO_SUCH_FILE if bad else results

    def open(self, path, flags, attr):
        path = self.files.normalize(path)
        try:
            fobj = self.files[path]
        except KeyError:
            if flags & os.O_WRONLY:
                # Only allow writes to files in existing directories.
                if os.path.dirname(path) not in self.files:
                    return paramiko.SFTP_NO_SUCH_FILE
                self.files[path] = fobj = FakeFile("", path)
            # No write flag means a read, which means they tried to read a
            # nonexistent file.
            else:
                return paramiko.SFTP_NO_SUCH_FILE
        f = FakeSFTPHandle()
        f.readfile = f.writefile = fobj
        return f

    def stat(self, path):
        path = self.files.normalize(path)
        logger.debug('stat: {}'.format(path))
        try:
            fobj = self.files[path]
        except KeyError:
            print "No Such File: {}".format(path)
            return paramiko.SFTP_NO_SUCH_FILE
        return fobj.attributes

    # Don't care about links right now
    lstat = stat

    def chattr(self, path, attr):
        path = self.files.normalize(path)
        if path not in self.files:
            return paramiko.SFTP_NO_SUCH_FILE
        # Attempt to gracefully update instead of overwrite, since things like
        # chmod will call us with an SFTPAttributes object that only exhibits
        # e.g. st_mode, and we don't want to lose our filename or size...
        for which in "size uid gid mode atime mtime".split():
            attname = "st_" + which
            incoming = getattr(attr, attname)
            if incoming is not None:
                setattr(self.files[path].attributes, attname, incoming)
        return paramiko.SFTP_OK

    def mkdir(self, path, attr):
        self.files[path] = None
        return paramiko.SFTP_OK
