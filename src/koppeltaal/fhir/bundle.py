import uuid

from koppeltaal.fhir import resource
from koppeltaal import (interfaces, utils)


MARKER = object()


class BundleEntry(resource.ResourceEntry):
    _atom_id = MARKER

    def __init__(self, bundle, entry=None, model=None):
        if entry is not None:
            self._fhir_link = utils.json2links(entry).get('self')
            self._atom_id = entry['id']

            super(BundleEntry, self).__init__(
                bundle, resource=entry['content'])
        if model is not None:
            super(BundleEntry, self).__init__(
                bundle, model=model)

    @property
    def atom_id(self):
        if self._atom_id is not MARKER:
            return self._atom_id

        if self.fhir_link is not None:
            self._atom_id = utils.strip_history_from_link(self.fhir_link)
        else:
            self._atom_id = self._bundle.configuration.link(
                self._model, self.resource_type)
        return self._atom_id

    def pack(self):
        entry = {
            "content": super(BundleEntry, self).pack(),
            "id": self.atom_id}
        if self.fhir_link is not None:
            entry["link"] = [{"rel": "self", "href": self.fhir_link}]
        return entry


class Bundle(resource.Resource):
    entry_type = BundleEntry

    def add_payload(self, response):
        if response['resourceType'] != 'Bundle' or 'entry' not in response:
            raise interfaces.InvalidBundle(response)
        for entry in response['entry']:
            self.items.append(self.entry_type(self, entry=entry))

    def get_payload(self):
        assert self.domain is not None, 'Domain is required to create payloads'
        entries = list(self.pack())
        return {
            "resourceType": "Bundle",
            "id": "urn:uuid:{}".format(uuid.uuid4()),
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
