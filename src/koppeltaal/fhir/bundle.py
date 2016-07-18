import uuid

from koppeltaal.fhir import resource
from koppeltaal import (definitions, interfaces, utils)


MARKER = object()


class Entry(resource.Entry):
    _atom_id = MARKER

    def __init__(self, resource, entry=None, model=None):
        if entry is not None:
            self._fhir_link = utils.json2links(entry).get('self')
            self._atom_id = entry.get('id')

            super(Entry, self).__init__(
                resource, content=entry['content'])
        if model is not None:
            super(Entry, self).__init__(
                resource, model=model)

    @property
    def atom_id(self):
        if self._atom_id is not MARKER:
            return self._atom_id

        if self.fhir_link is not None:
            self._atom_id = utils.strip_history_from_link(self.fhir_link)
        else:
            self._atom_id = self._resource.configuration.link(
                self._model, self.resource_type)
        return self._atom_id

    def pack(self):
        entry = {
            "content": super(Entry, self).pack(),
            "id": self.atom_id}
        if self.fhir_link is not None:
            entry["link"] = [{"rel": "self", "href": self.fhir_link}]
        return entry


class Bundle(resource.Resource):
    entry_type = Entry

    def add_payload(self, response):
        if response['resourceType'] != 'Bundle' or 'entry' not in response:
            raise interfaces.InvalidBundle(self, response)
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

    def errors(self):
        errors = []
        for model in self.unpack():
            if interfaces.IBrokenFHIRResource.providedBy(model):
                errors.append(model)
        return errors

    def unpack_message_header(self):
        message = None
        for model in self.unpack():
            if definitions.MessageHeader.providedBy(model):
                if message is not None:
                    # We allow only one message header in the bundle.
                    raise interfaces.InvalidBundle(self)
                message = model
        return message
