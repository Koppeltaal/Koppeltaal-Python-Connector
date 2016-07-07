
import json

from koppeltaal.fhir import packaging
from koppeltaal import (
    fhir,
    codes,
    interfaces)


MARKER = object()


class ResourceEntry(object):
    _model = MARKER
    _content = MARKER
    resource_type = None
    fhir_link = None
    fhir_unversioned_link = None

    def __init__(self, bundle, resource=None, model=None):
        self._bundle = bundle

        if resource is not None:
            self._content = resource.copy()
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

        return self._content

    def __eq__(self, other):
        if isinstance(other, dict):
            return other.get('reference', None) in (
                self.fhir_link, self.fhir_unversioned_link)
        if interfaces.IFHIRResource.providedBy(other):
            return other.fhir_link == self.fhir_link
        return NotImplemented()

    def __format__(self, _):
        return ('<ResourceEntry fhir_link="{}" type="{}">'
                '{}</ResourceEntry>'.format(
                    self.fhir_link,
                    self.resource_type,
                    json.dumps(self._content, indent=2, sort_keys=True)))


class Resource(object):

    def __init__(self, domain=None, configuration=None):
        self.items = []
        self.domain = domain
        self.configuration = configuration

    def add_payload(self, response):
        self.items.append(ResourceEntry(self, resource=response))

    def add_model(self, model):
        assert interfaces.IFHIRResource.providedBy(model), \
            'Can only add resources to a bundle'
        entry = self.find(model)
        if entry is None:
            entry = ResourceEntry(self, model=model)
            self.items.append(entry)
        return entry

    def find(self, entry):
        for item in self.items:
            if entry == item:
                # ResourceEntry provides a smart "comparison".
                return item
        return None

    def pack(self):
        for item in self.items:
            yield item.pack()

    def get_payload(self):
        for payload in self.pack():
            return payload

    def unpack(self):
        for item in self.items:
            yield item.unpack()
