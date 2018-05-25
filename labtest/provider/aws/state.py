# -*- coding: utf-8 -*-
import os
import json
from fabric.api import env, run
from fabric.contrib.files import exists
from fabric.context_managers import settings
from labtest import filesystem
from labtest.provider.base_state import BaseState


class NotInCacheException(LookupError):
    pass


class S3State(BaseState):
    """
    Implements retrieval of state information from S3 and optionally a local cache
    """
    default_config = {
        'cache': True,
        'cache_path': '/testing/state/',
    }

    def _instantiate_cache(self):
        """
        Create the directory for the cache if it doesn't exist
        """
        if not exists(self.cache_path):
            filesystem.create_dir(self.cache_path)

    def _get_from_cache(self, key):
        """
        Looks in the local cache for the key and returns it. Raises exception if not found

        Args:
            key: The key to get

        Raises:
            NotInCacheException: If the key is not in the cache. This is to differentiate
                from a successful retrieval of a key from cache with a ``None`` value.

        Returns:
            Value of the found key
        """
        if self.cache:
            self._instantiate_cache()
            path = os.path.join(self.cache_path, key.lstrip('/'))
            if exists(path) and not filesystem.is_dir(path):
                return unicode(filesystem.get_file_contents(path).getvalue())

        raise NotInCacheException()

    def _is_in_s3(self, key):
        """
        Is the key in S3?

        Args:
            key: The key

        Returns:
            boolean
        """
        key = key.strip('/')
        cmd = [
            'aws s3api list-objects-v2',
            '--bucket',
            self.bucket,
            '--prefix',
            key,
            '--query "Contents[*].[Key][]"',
            '--output json'
        ]
        result = run(' '.join(cmd), quiet=env.quiet)
        return key in json.loads(result)

    def _get_local_file_path(self, key):
        """
        Given a key, return the full path in which to store the file

        If ``cache`` is ``True`` it will be the cache path, otherwise
        it will be a tmp file

        Args:
            key: the key to base the path on

        Returns:
            The full path
        """
        if self.cache:
            path = os.path.join(self.cache_path, key.lstrip('/'))
            basepath = os.path.dirname(path)
            filesystem.create_dir(basepath)
            return path
        else:
            return run('mktemp', quiet=env.quiet)

    def get(self, key):
        """
        Get the value of ``key`` from ``bucket`` navigating the hierarchy of the key path

        Args:
            key:     The key, as a ``/`` delimited path.

        Returns:
            The value or ``None``
        """
        for k in self._calc_search_paths(key):
            try:
                return self._get_from_cache(k)
            except NotInCacheException:
                if self._is_in_s3(k):
                    break
        path = self._get_local_file_path(k)  # This is the path actually found

        with settings(warn_only=True):
            run('aws s3api get-object --bucket {bucket} --key {key} {cache_path}'.format(
                bucket=self.bucket,
                key=k.lstrip('/'),
                cache_path=path), quiet=env.quiet)
            return unicode(filesystem.get_file_contents(path).getvalue())
        return None
