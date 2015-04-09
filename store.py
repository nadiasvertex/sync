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

    def get(self, key):
        """
        Get the value associated with the key.
        :param key: The key to look up.
        :return: A tuple of (version, value) stored.
        """
        return self.data.get(key, (None, None, None))[1:]

    def put(self, key, value):
        """
        Updates the current value associated with this key. Also stores when the value
        was last written, and a serial number indicating what the current version of the
        value is.

        :param key: The key to store.
        :param value: The value to store.
        :return: The previous value.
        """
        current_value = self.data.get(key, (None, -1, None))
        self.data[key] = (datetime.now(), current_value[1] + 1, value)
        return current_value[2]

    def put_atomic(self, expected_version, key, value):
        """
        If the version of the value in the system is what we expect, then update the key with
        the value given. Otherwise return a tuple of (False, cur_serial, cur_value).

        :param expected_version: The version of the record we expect.
        :param key: The key to update.
        :param value: The value to associate with the key.
        :return: A tuple of (True, new_version, new_value) if it works
        """
        current_value = self.data.get(key, (None, -1, None))
        if current_value[1] != expected_version:
            return False, current_value[1], current_value[2]

        self.data[key] = (datetime.now(), current_value[1]+1, value)
        return True, current_value[1] + 1, value
