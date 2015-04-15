import json
from pprint import pprint
import uuid
from datetime import datetime

__author__ = 'Christopher Nelson'


class Annotations:
    def __init__(self, store):
        self.store = store

    def _merge_dict(self, d1, d2, o):
        """
        Merges dictionaries d1 and d2. Expects each dictionary to have a set of keys whose values are also dictionaries.
        Those dictionaries must have a key called "when", which orders the values based on simple equality.

        :param d1: A dictionary.
        :param d2: A different dictionary.
        :param o: The output object.
        :return: The set union of d1 and d2, with conflicts resolved by timestamp.
        """
        keys = set(d1.keys()).union(set(d2.keys()))

        for item in keys:
            d1_item = d1.get(item)
            d2_item = d2.get(item)
            if d1_item is None:
                o[item] = d2_item
            elif d2_item is None:
                o[item] = d1_item
            else:
                d1_when = d1_item["when"]
                d2_when = d2_item["when"]
                o[item] = d1_item if d1_when > d2_when else d2_item

        return o

    def _merge(self, d1, d2):
        """
        Merges data from d1 and d2, returns the results.

        :param d1: An annotation dictionary.
        :param d2: A different annotation dictionary.
        :return: The set union of d1 and d2, conflict resolved by timestamp.
        """
        if d1 is None:
            return d2
        if d2 is None:
            return d1

        d1_h = d1["highlights"]
        d2_h = d2["highlights"]

        d1_n = d1["notes"]
        d2_n = d2["notes"]

        return {
            "highlights": self._merge_dict(d1_h, d2_h, {}),
            "notes": self._merge_dict(d1_n, d2_n, {})
        }


    def _fetch_annotations(self, user_id, publication, key, o, children, data):
        """
        Recursively constructs a dictionary with

        :param user_id: The user id to select.
        :param publication: The publication to select.
        :param key: The key to use for finding children.
        :param o: The output object to write results into.
        :param children: The children to examine for data.
        :param data: The data retrieved for the 'key' parameter.
        :return: The output object.
        """
        if data is not None:
            o[key] = data

        for item in children:
            c_key = "%s:%s" % (key, item)
            children, data = self.store.get_children(user_id, publication, c_key)
            self._fetch_annotations(user_id, publication, c_key, o, children, data)

        return o


    def _get_key(self, pub, citation):
        kind, position = citation.split("/")
        p_vec = position.split(":")
        if kind == "doc" and len(p_vec) >= 3:
            p_vec = p_vec[0:2]
        elif kind == "bible" and len(p_vec) >= 4:
            p_vec = p_vec[0:3]
        key = "%s/%s/%s" % (pub, kind, "/".join(p_vec))
        return key

    def get(self, user_id, publication, citation):
        """
        Returns all the annotations for the given citation. The citation can
        be specified at varying degrees of precision. If you specify a document only,
        it will return all annotations for that document. If you specify a paragraph,
        it will return annotations for that paragraph only. The same works for a
        bible chapter and verse. The limit of precision is offset. It's not possible
        to ask for all annotations covering some offset.

        :param user_id: The user id to select.
        :param publication: The publication to select.
        :param citation: The citation to select.
        :return: The annotation structures.
        """
        key = self._get_key(publication, citation)
        children, data = self.store.get_children(user_id, "annotation", key)

        return self._fetch_annotations(user_id, publication, key, {}, children, data)

    def add_highlight(self, user_id, publication, citation, highlight, note=None):
        """
        Adds a highlight to this citation.


        TODO: Perform highlight merging.

        :param user_id: The user id to select.
        :param publication: The publication to select.
        :param citation: The citation to select.
        :param highlight: The highlight to add.
        :param note: The note to attach to the highlight. Optional
        :return: (highlight_id, version, citation_annotation_data)
        """
        key = self._get_key(publication, citation)
        version, raw_data = self.store.get(user_id, "annotation", key)
        when = datetime.now().isoformat()
        while True:
            data = {} if raw_data is None else json.loads(raw_data)
            highlights = data.setdefault("highlights", {})

            if note is not None:
                notes = data.setdefault("notes", {})
                note_id = str(uuid.uuid4())
                notes[note_id] = {"text": note, "when": when}
            else:
                note_id = None

            h_id = str(uuid.uuid4())
            highlights[h_id] = {"range": highlight, "note-id": note_id, "when": when}

            new_data = json.dumps(data)
            worked, next_version, value = self.store.put(user_id, "annotation", version, key, new_data)
            if worked:
                return {
                    "highlight-id": h_id,
                    "version": next_version,
                    "annotations": value
                }

    def add_note(self, user_id, publication, citation, note):
        """
        Adds a note to this citation.

        :param user_id: The user id to select.
        :param publication: The publication to select.
        :param citation: The citation to select.
        :param note: The note to add.
        :return: (note_id, version, citation_annotation_data)
        """
        key = self._get_key(publication, citation)
        version, raw_data = self.store.get(user_id, "annotation", key)
        when = datetime.now().isoformat()
        while True:
            data = {} if raw_data is None else json.loads(raw_data)
            notes = data.setdefault("notes", {})
            note_id = str(uuid.uuid4())
            notes[note_id] = {"text": note, "when": when}

            new_data = json.dumps(data)
            worked, next_version, value = self.store.put(user_id, "annotation", version, key, new_data)
            if worked:
                return {
                    "note-id": note_id,
                    "version": next_version,
                    "annotations": value
                }

    def update(self, user_id, publication, citation, data):
        """
        Merges the annotation data stored at `citation` with the data given to us in
        `data`. A set union is performed, and any intersections are resolved by using
        the latest timestamp as the victor.

        :param user_id: The user id to select.
        :param publication: The publication to select.
        :param citation: The citation to select.
        :param data: The annotation data for this citation.
        :return: (version, merged_annotation_data)
        """
        pprint(data)
        worked = False
        key = self._get_key(publication, citation)
        version, raw_data = self.store.get(user_id, "annotation", key)
        while True:
            pprint((worked, version, raw_data))
            current_data = json.loads(raw_data) if raw_data else None
            pprint(current_data)
            if worked:
                return {
                    "version": version,
                    "data": current_data
                }

            worked, version, raw_data = self.store.put(
                user_id, "annotation", version, key,
                json.dumps(self._merge(current_data, data)).encode("utf-8")
            )


