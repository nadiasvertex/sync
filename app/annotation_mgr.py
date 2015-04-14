import json
import uuid

__author__ = 'Christopher Nelson'


class Annotations:
    def __init__(self, store):
        self.store = store

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
        kind, position = citation.split("/")
        p_vec = position.split(":")
        if kind == "doc" and len(p_vec) >= 3:
            p_vec = p_vec[0:2]
        elif kind == "bible" and len(p_vec) >= 4:
            p_vec = p_vec[0:3]

        key = "annotation/%s/%s" % (kind, "/".join(p_vec))
        children, data = self.store.get_children(user_id, publication, key)

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
        version, raw_data = self.store.get(user_id, publication, citation)
        while True:
            data = {} if raw_data is None else json.loads(raw_data)
            highlights = data.setdefault("highlights", {})

            if note is not None:
                notes = data.setdefault("notes", {})
                note_id = uuid.uuid4()
                notes[note_id] = note
            else:
                note_id = None

            h_id = uuid.uuid4()
            highlights[h_id] = {"range": highlight, "note-id": note_id}

            new_data = json.dumps(data)
            worked, next_version, value = self.store.put(user_id, "annotation", version, citation, new_data)
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
        version, raw_data = self.store.get(user_id, publication, citation)
        while True:
            data = {} if raw_data is None else json.loads(raw_data)
            notes = data.setdefault("notes", {})
            note_id = uuid.uuid4()
            notes[note_id] = note

            new_data = json.dumps(data)
            worked, next_version, value = self.store.put(user_id, "annotation", version, citation, new_data)
            if worked:
                return {
                    "note-id": note_id,
                    "version": next_version,
                    "annotations": value
                }
