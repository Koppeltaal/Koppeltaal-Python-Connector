# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

from koppeltaal.fhir import resource
from koppeltaal import (interfaces, utils)


MARKER = object()


class Entry(resource.Entry):
    _atom_id = MARKER

    def __init__(self, packer, entry=None, model=None):
        if entry is not None:
            self._fhir_link = utils.json2links(entry).get('self')
            self._atom_id = entry.get('id')

            super(Entry, self).__init__(packer, content=entry['content'])
        if model is not None:
            super(Entry, self).__init__(packer, model=model)

    @property
    def atom_id(self):
        if self._atom_id is not MARKER:
            return self._atom_id

        link = self.fhir_link
        if link is None:
            link = self._packer.fhir_link(self._model, self.resource_type)
        self._atom_id = utils.strip_history_from_link(link)
        return self._atom_id

    def pack(self):
        entry = {
            "content": super(Entry, self).pack(),
            "id": self.atom_id}
        if self.fhir_link is not None:
            entry["link"] = [{"rel": "self", "href": self.fhir_link}]
        return entry

    def __eq__(self, other):
        if isinstance(other, dict) and 'reference' in other:
            return other['reference'] in filter(
                None,
                (self.history_less_fhir_link, self.fhir_link, self.atom_id))
        return super(Entry, self).__eq__(other)


class Bundle(resource.Resource):
    _create_entry = Entry

    def add_payload(self, response):
        if response['resourceType'] != 'Bundle' or 'entry' not in response:
            raise interfaces.InvalidBundle(self, response)
        for entry in response['entry']:
            self.items.append(self._create_entry(self.packer, entry=entry))

    def get_payload(self):
        assert self.domain is not None, 'Domain is required to create payloads'
        entries = list(self.pack())
        return {
            "resourceType": "Bundle",
            "id": "urn:uuid:{}".format(utils.uniqueid()),
            "updated": utils.now().isoformat(),
            "category": [{
                "term": "{}Domain#{}".format(
                    interfaces.NAMESPACE, self.domain),
                "label": self.domain,
                "scheme": "http://hl7.org/fhir/tag/security"
            }, {
                "term": "http://hl7.org/fhir/tag/message",
                "scheme": "http://hl7.org/fhir/tag"
            }],
            "entry": entries}

    def errors(self):
        errors = []
        for model in self.unpack():
            if interfaces.IBrokenFHIRResource.providedBy(model):
                errors.append(model)
        return errors
