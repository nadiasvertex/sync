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

    def __init__(self, host_list):
        hosts = ",".join(host_list)
        print("zk, connecting to: '%s'" % hosts)
        self.zk = KazooClient(hosts)

    def __enter__(self):
        self.zk.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
        print("zk, fetching: '%s'" % path)
        try:
            r = self.zk.get(path)
            print("zk, value at: '%s'='%s'" % (path, r))
            return r[1].version, r[0]
        except NoNodeError:
            print("zk, no value at: '%s'" % path)
            return None, None


    def put(self, uid, ns, expected_version, key, value):
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
        self.zk.ensure_path(path)

        if expected_version is None:
            self.zk.set(path, value)
            return True, 1, value

        try:
            print("zk, set '%s'='%s'" % (path, value))
            self.zk.set(path, value, version=expected_version)
            return True, expected_version + 1, value
        except BadVersionError:
            print("zk, set failed '%s'='%s'" % (path, value))
            r = self.zk.get(path)
            return False, r[1].version, r[0]

