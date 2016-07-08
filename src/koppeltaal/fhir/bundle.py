
import json
import uuid

from koppeltaal.fhir import packaging
from koppeltaal import (
    fhir,
    codes,
    interfaces,
    utils)


MARKER = object()


class BundleEntry(object):
    _model = MARKER
    _content = MARKER
    resource_type = None
    fhir_link = None
    fhir_unversioned_link = None

    def __init__(self, bundle, entry=None, model=None):
        self._bundle = bundle

        if entry is not None:
            self.fhir_link = utils.json2links(entry).get('self')
            self.fhir_unversioned_link = entry['id']

            self._content = entry['content'].copy()
            resource_type = self._content.get('resourceType', 'Other')
            if resource_type == 'Other':
                assert 'code' in self._content
                for code in self._content.get('code').get('coding', []):
                    resource_type = codes.OTHER_RESOURCE_USAGE.unpack_coding(
                        code)
            assert resource_type != 'Other'
            self.resource_type = resource_type
        if model is not None:
            self._model = model

    def unpack(self):
        if self._model is not MARKER:
            return self._model

        self._model = None
        definition = fhir.REGISTRY.definition_for_type(self.resource_type)
        if definition is not None:
            self._model = packaging.unpack(
                self._content, definition, self._bundle)
            if self._model is not None:
                self._model.fhir_link = self.fhir_link
        return self._model

    def pack(self):
        if self._content is MARKER:
            definition = fhir.REGISTRY.definition_for_model(self._model)
            if definition is None:
                raise interfaces.InvalidValue(None, self._model)
            self._content = packaging.pack(
                self._model, definition, self._bundle)
            type_definition = fhir.REGISTRY.type_for_definition(definition)
            self.resource_type = type_definition[0]
            if type_definition[1]:
                # This is not a standard fhir resource type.
                self._content['resourceType'] = 'Other'
                self._content['code'] = {
                    'coding': [
                        codes.OTHER_RESOURCE_USAGE.pack_coding(
                            self.resource_type)]}
            else:
                self._content['resourceType'] = self.resource_type
            self.fhir_link = self._model.fhir_link
            if (interfaces.IIdentifiedFHIRResource.providedBy(self._model) and
                    self.fhir_link is None):
                self.fhir_link = self._bundle.configuration.link(
                    self._model, self.resource_type)

        entry = {
            "content": self._content}
        if self.fhir_link is not None:
            entry.update({
                "id": utils.strip_history_from_link(self.fhir_link),
                "links": [{"rel": "self",
                           "url": self.fhir_link}]})
        return entry

    def __eq__(self, other):
        if isinstance(other, dict):
            return other.get('reference', None) in (
                self.fhir_link, self.fhir_unversioned_link)
        if interfaces.IFHIRResource.providedBy(other):
            if self._model is not MARKER:
                return self._model is other
            assert self.fhir_link is not None, 'Should not happen'
            return other.fhir_link == self.fhir_link

        return NotImplemented()

    def __format__(self, _):
        return '<BundleEntry fhir_link="{}" type="{}">{}</BundleEntry>'.format(
            self.fhir_link,
            self.resource_type,
            json.dumps(self._content, indent=2, sort_keys=True))


class Bundle(object):

    def __init__(self, domain=None, configuration=None):
        self.items = []
        self.domain = domain
        self.configuration = configuration

    def add_payload(self, response):
        if response['resourceType'] != 'Bundle':
            raise interfaces.InvalidBundle(response)
        for entry in response['entry']:
            self.items.append(BundleEntry(self, entry=entry))

    def add_model(self, model):
        assert interfaces.IFHIRResource.providedBy(model), \
            'Can only add resources to a bundle'
        entry = self.find(model)
        if entry is None:
            entry = BundleEntry(self, model=model)
            self.items.append(entry)
        return entry

    def find(self, entry):
        for item in self.items:
            if entry == item:
                # BundleEntry provides a smart "comparison".
                return item
        return None

    def pack(self):
        for item in self.items:
            yield item.pack()

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

    def unpack(self):
        for item in self.items:
            yield item.unpack()
