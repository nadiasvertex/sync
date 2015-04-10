"""
Provides a key-value store interface for couchbase.
"""

from couchbase.bucket import Bucket
from couchbase.exceptions import NotFoundError, KeyExistsError

__author__ = 'Christopher Nelson'


class Store:
    """
    Uses couchbase as a key value store. This store is as thread safe as the underlying client.
    """

    def __init__(self, host_list):
        hosts = ",".join(host_list)
        uri = "couchbase://%s/sync-app" % hosts
        print("cb, connecting to: '%s'" % uri)
        self.cb = Bucket(uri, password=None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get(self, uid, ns, key):
        """
        Get the value associated with the key.
        :param uid: The user id to use.
        :param ns: The namespace to use.
        :param key: The key to look up.
        :return: A tuple of (version, value) stored.
        """
        path = "%s/%s/%s" % (uid, ns, key)
        print("cb, fetching: '%s'" % path)
        try:
            r = self.cb.get(path)
            print("cb, value at: '%s'='%s'" % (path, r))
            return r.cas, r.value
        except NotFoundError:
            print("cb, no value at: '%s'" % path)
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
        path = "%s/%s/%s" % (uid, ns, key)

        if expected_version is None:
            r = self.cb.upsert(path, value)
            return True, r.cas, value

        try:
            print("cb, set '%s'='%s'" % (path, value))
            r = self.cb.upsert(path, value, cas=expected_version)
            return True, r.cas, value
        except KeyExistsError:
            print("cb, set failed '%s'='%s'" % (path, value))
            r = self.cb.get(path)
            return False, r.cas, r.value

