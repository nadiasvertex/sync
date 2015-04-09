"""
Manages bookmarks. Provides synchronization between versions.
"""
import json

__author__ = 'Christopher Nelson'

class Bookmarks:
    def __init__(self, store):
        self.store = store

    def merge(self, b1, b2):
        """
        Perform a bookmark merge. The dataset is a dictionary of bookmarks, the keys are the slots
        from 0 to 9.

        The bookmark merge is very simple. If an item exists in b1 or b2, but not both, the item is simply
        copied over.

        Each bookmark item has two important keys: The value, and when the value was set. If value is set to None
        then the item was deleted. The "when" component is the final arbiter. The when keys of each item are
        compared, and the one which is newer wins.

        The when component is expected to be an iso8601 timestamp in the GMT timezone.

        :param b1: Bookmark payload one to merge.
        :param b2: Bookmark payload two to merge.
        :return: The merged bookmarks.
        """
        dest = {}
        for slot in range(0, 9):
            if slot in b1 and slot in b2:
                b1_slot = b1[slot]
                b2_slot = b2[slot]
                b1_when = b1_slot["when"]
                b2_when = b2_slot["when"]

                # Perform the assignment, and then delete the result if needed.
                dest[slot] = b1_slot if b1_when > b2_when else b2_slot
                if dest[slot]["value"] is None:
                    del dest[slot]

            elif slot in b1 and b1[slot]["value"] is not None:
                dest[slot] = b1[slot]

            elif slot in b2 and b2[slot]["value"] is not None:
                dest[slot] = b2[slot]

    def get(self, user_id, publication):
        r = self.store.get(user_id, "bookmark", publication)
        if r[1] is None:
            return None

        return json.loads(r[1])

    def update(self, user_id, publication, bookmarks):
        worked = False
        version, value = self.store.get(user_id, "bookmark", publication)

        while True:
            stored_bookmarks = json.loads(value)
            if worked:
                return stored_bookmarks

            worked, version, value = self.store.put_atomic(
                user_id,
                "bookmark",
                version,
                publication,
                json.dumps(self.merge(bookmarks, stored_bookmarks))
            )

