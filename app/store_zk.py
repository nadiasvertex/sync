"""
Provides a key-value store interface for zookeeper.
"""

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError, BadVersionError

__author__ = 'Christopher Nelson'


class Store:
    """
    Uses zoo keeper as a key vaue store. This store is as thread safe as the underlying client.
    """

    def __init__(self, hosts):
        self.zk = KazooClient(hosts=",".join(hosts))
        self.zk.start()

    def __del__(self):
        self.zk.stop()

    def get(self, uid, ns, key):
        """
        Get the value associated with the key.
        :param uid: The user id to use.
        :param ns: The namespace to use.
        :param key: The key to look up.
        :return: A tuple of (version, value) stored.
        """
        path = "/jwl/sync/%s/%s/%s" % (uid, ns, key)
        try:
            r = self.zk.get(path)
            return r[1].version, r[0]
        except NoNodeError:
            return None, None

    def put(self, uid, ns, key, value):
        """
        Updates the current value associated with this key. Also stores when the value
        was last written, and a serial number indicating what the current version of the
        value is.

        :param uid: The user id to use.
        :param ns: The namespace to use.
        :param key: The key to store.
        :param value: The value to store.
        :return: The previous value.
        """
        path = "/jwl/sync/%s/%s/%s" % (uid, ns, key)
        self.zk.ensure_path(path)
        self.zk.set(path, value)


    def put_atomic(self, uid, ns, expected_version, key, value):
        """
        If the version of the value in the system is what we expect, then update the key with
        the value given. Otherwise return a tuple of (False, cur_serial, cur_value).

        :param uid: The user id to use.
        :param ns: The namespace to use.
        :param expected_version: The version of the record we expect.
        :param key: The key to update.
        :param value: The value to associate with the key.
        :return: A tuple of (True, new_version, new_value) if it works, (False, cur_version, cur_value) on failure.
        """
        path = "/jwl/sync/%s/%s/%s" % (uid, ns, key)
        try:
            self.zk.set(path, value, version=expected_version)
            return True, expected_version+1, value
        except BadVersionError:
            r = self.zk.get(path)
            return False, r[1].version, r[0]

