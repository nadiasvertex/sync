"""
Provides a basic key-value store interface. This can be replaced by any similar kind of storage interface.
"""

__author__ = 'Christopher Nelson'

from datetime import datetime


class Store:
    """
    Simulates a simple key value store. This store is not safe or atomic in the presence
    of multiple threads.
    """

    def __init__(self):
        self.data = {}

    def _get_key(self, uid, ns, key):
        return "%s:%s:%s" % (uid, ns, key)

    def get(self, uid, ns, key):
        """
        Get the value associated with the key.
        :param uid: The user id to use.
        :param ns: The namespace to use.
        :param key: The key to look up.
        :return: A tuple of (version, value) stored.
        """
        return self.data.get(self._get_key(uid, ns, key), (None, None, None))[1:]


    def put(self, uid, ns, expected_version, key, value):
        """
        If the version of the value in the system is what we expect, then update the key with
        the value given. Otherwise return a tuple of (False, cur_serial, cur_value).

        :param uid: The user id to use.
        :param ns: The namespace to use.
        :param expected_version: The version of the record we expect.
        :param key: The key to update.
        :param value: The value to associate with the key.
        :return: A tuple of (True, new_version, new_value) if it works
        """
        raw_key = self._get_key(uid, ns, key)
        current_value = self.data.get(raw_key, (None, -1, None))
        if current_value[1] != expected_version:
            return False, current_value[1], current_value[2]

        self.data[raw_key] = (datetime.now(), current_value[1] + 1, value)
        return True, current_value[1] + 1, value
