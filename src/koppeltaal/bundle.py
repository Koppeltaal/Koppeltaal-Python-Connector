import datetime
import dateutil.parser
import json
import uuid
import zope.interface

from koppeltaal import (
    codes,
    definitions,
    interfaces,
    models,
    utils)


MARKER = object()


class Registry(dict):

    def definition_for_type(self, resource_type):
        definitions = []
        for definition in self.keys():
            defined_type = definition.queryTaggedValue('resource type')
            if defined_type and defined_type[0] == resource_type:
                definitions.append(definition)
        assert len(definitions) < 2, 'Too many definitions for resource type'
        if definitions:
            return definitions[0]
        return None

    def model_for_definition(self, definition):
        return self.get(definition)

    def definition_for_model(self, model):
        definitions = [
            d for d in zope.interface.providedBy(model).interfaces()
            if d in self]
        assert len(definitions) < 2, \
            'Too many definitions implemented by model'
        if definitions:
            return definitions[0]
        return None

    def type_for_definition(self, definition):
        assert definition in self, 'Unknown definition'
        return definition.queryTaggedValue('resource type')

    def type_for_model(self, model):
        definition = self.definition_for_model()
        if definition is None:
            return None
        return definition.queryTaggedValue('resource type')


REGISTRY = Registry({
    definitions.Activity: models.Activity,
    definitions.ActivityDefinition: models.ActivityDefinition,
    definitions.CarePlan: models.CarePlan,
    definitions.Goal: models.Goal,
    definitions.MessageHeader: models.MessageHeader,
    definitions.Name: models.Name,
    definitions.Participant: models.Participant,
    definitions.Patient: models.Patient,
    definitions.Practitioner: models.Practitioner,
    definitions.ProcessingStatus: models.Status,
    definitions.Source: models.Source,
    definitions.SubActivity: models.SubActivity,
    definitions.SubActivityDefinition: models.SubActivityDefinition,
})


class Extension(object):

    def __init__(self, bundle, content=None):
        self._bundle = bundle
        self._index = {}
        if content and 'extension' in content:
            for extension in content['extension']:
                url = extension['url']
                self._index.setdefault(url, []).append(extension)

    def _unpack_item(self, field, extension):
        if field.field_type == 'boolean':
            value = extension.get('valueBoolean')
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'code':
            value = extension.get('valueCode')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return field.binding.unpack_code(value)

        if field.field_type == 'coding':
            value = extension.get('valueCoding')
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            return field.binding.unpack_coding(value)

        if field.field_type == 'date':
            value = extension.get('valueDate')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value).date()

        if field.field_type == 'datetime':
            value = extension.get('valueDateTime')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

        if field.field_type == 'instant':
            value = extension.get('valueInstant')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

        if field.field_type == 'integer':
            value = extension.get('valueInteger')
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'object':
            value = extension.get('extension')
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
            return unpack(extension, field.binding, self._bundle)

        if field.field_type == 'reference':
            value = extension.get('valueResource')
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            reference = self._bundle.find(value)
            if reference:
                return reference.unpack()
            return None

        if field.field_type == 'string':
            value = extension.get('valueString')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def unpack(self, field):
        if field.url not in self._index:
            if field.optional:
                if field.multiple is definitions.ALL_ITEMS:
                    return []
                return None
            raise interfaces.RequiredMissing(field)
        extensions = self._index[field.url]
        if field.multiple is definitions.ALL_ITEMS:
            values = []
            for extension in extensions:
                values.append(self._unpack_item(field, extension))
            return values

        if not field.multiple and len(extensions) != 1:
            raise interfaces.InvalidValue(field)
        return self._unpack_item(field, extensions[0])

    @property
    def content(self):
        all_extensions = []
        for extensions in self._index.values():
            all_extensions.extend(extensions)
        return {"extension": all_extensions}

    def _pack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return {'valueBoolean': value}

        if field.field_type == 'code':
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return {'valueCode': field.binding.pack_code(value)}

        if field.field_type == 'coding':
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return {'valueCoding': field.binding.pack_coding(value)}

        if field.field_type == 'date':
            if not isinstance(value, datetime.date):
                raise interfaces.InvalidValue(field, value)
            return {'valueDate': value.isoformat()}

        if field.field_type == 'datetime':
            if not isinstance(value, datetime.datetime):
                raise interfaces.InvalidValue(field, value)
            return {'valueDateTime': value.isoformat()}

        if field.field_type == 'instant':
            if not isinstance(value, datetime.datetime):
                raise interfaces.InvalidValue(field, value)
            if value.tzinfo is None:
                # We need a timezone!
                # XXX maybe automatically add UTC.
                raise interfaces.InvalidValue(field, value)
            return {'valueInstant': value.isoformat()}

        if field.field_type == 'integer':
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return {'valueInteger': value}

        if field.field_type == 'object':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            return pack(value, field.binding, self._bundle)

        if field.field_type == 'reference':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            raise NotImplementedError()
            self._bundle.pack(value)

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return {'valueString': value}

        raise NotImplementedError()

    def pack(self, field, value):
        if value is None:
            if not field.optional:
                raise interfaces.InvalidValue(field, value)
            return
        if field.multiple is definitions.ALL_ITEMS:
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
        else:
            value = [value]
        for single_value in value:
            extension = {"url": field.url}
            extension.update(self._pack_item(field, single_value))
            self._index.setdefault(field.url, []).append(extension)


class Native(object):

    def __init__(self, bundle, content=None):
        self._bundle = bundle
        self._content = content or {}

    @property
    def content(self):
        return self._content.copy()

    def _unpack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'codable':
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            if 'coding' not in value:
                raise interfaces.InvalidValue(field, value)
            if not isinstance(value['coding'], list):
                raise interfaces.InvalidValue(field, value)
            if len(value['coding']) != 1:
                raise interfaces.InvalidValue(field, value)
            return field.binding.unpack_coding(value['coding'][0])

        if field.field_type == 'code':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return field.binding.unpack_code(value)

        if field.field_type == 'coding':
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            return field.binding.unpack_coding(value)

        if field.field_type == 'date':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value).date()

        if field.field_type == 'datetime':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

        if field.field_type == 'instant':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

        if field.field_type == 'integer':
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'object':
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            return unpack(value, field.binding, self._bundle)

        if field.field_type == 'reference':
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            reference = self._bundle.find(value)
            if reference is not None:
                return reference.unpack()
            return None

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def unpack(self, field):
        if field.name not in self._content:
            if field.optional:
                if field.multiple is definitions.ALL_ITEMS:
                    return []
                return None
            raise interfaces.RequiredMissing(field)

        value = self._content[field.name]
        if field.multiple:
            # If the field is multiple there is a list of item. We
            # only support the first one at the moment.
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
            if not len(value):
                raise interfaces.RequiredMissing(field)
            if field.multiple is definitions.ALL_ITEMS:
                return [self._unpack_item(field, v) for v in value]
            value = value[0]
        return self._unpack_item(field, value)

    def _pack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'codable':
            if isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return {"coding": [field.binding.pack_coding(value)]}

        if field.field_type == 'code':
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return field.binding.pack_code(value)

        if field.field_type == 'coding':
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return field.binding.pack_coding(value)

        if field.field_type == 'date':
            if not isinstance(value, datetime.date):
                raise interfaces.InvalidValue(field, value)
            return value.isoformat()

        if field.field_type == 'datetime':
            if not isinstance(value, datetime.datetime):
                raise interfaces.InvalidValue(field, value)
            return value.isoformat()

        if field.field_type == 'instant':
            if not isinstance(value, datetime.datetime):
                raise interfaces.InvalidValue(field, value)
            if value.tzinfo is None:
                # We need a timezone!
                # XXX maybe automatically add UTC.
                raise interfaces.InvalidValue(field, value)
            return value.isoformat()

        if field.field_type == 'integer':
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'object':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            return pack(value, field.binding, self._bundle)

        if field.field_type == 'reference':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            raise NotImplementedError()
            self._bundle.pack(value)

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def pack(self, field, value):
        if value is None:
            if not field.optional:
                raise interfaces.InvalidValue(field, value)
            return
        if field.multiple is definitions.ALL_ITEMS:
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
            item = [self._pack_item(field, v) for v in value]
        elif field.multiple is definitions.FIRST_ITEM:
            item = [self._pack_item(field, value)]
        else:
            assert field.multiple is False
            item = self._pack_item(field, value)
        self._content[field.name] = item


def unpack(item, definition, bundle):
    factory = REGISTRY.model_for_definition(definition)
    if factory is None:
        return None
    model = factory()

    extension = Extension(bundle, item)
    native = Native(bundle, item)
    for name, field in definition.namesAndDescriptions():
        if not isinstance(field, definitions.Field):
            continue
        if field.extension is None:
            setattr(model, name, native.unpack(field))
        else:
            setattr(model, name, extension.unpack(field))
    return model


def pack(model, definition, bundle):
    extension = Extension(bundle)
    native = Native(bundle)

    if not definition.providedBy(model):
        raise interfaces.InvalidValue(definition, model)

    for name, field in definition.namesAndDescriptions():
        if not isinstance(field, definitions.Field):
            continue
        value = getattr(model, name, None)
        if field.extension is None:
            native.pack(field, value)
        else:
            extension.pack(field, value)
    item = {}
    item.update(extension.content)
    item.update(native.content)
    return item


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
        definition = REGISTRY.definition_for_type(self.resource_type)
        if definition is not None:
            self._model = unpack(self._content, definition, self._bundle)
            if self._model is not None:
                self._model.fhir_link = self.fhir_link
        return self._model

    def pack(self):
        if self._content is MARKER:
            definition = REGISTRY.definition_for_model(self._model)
            if definition is None:
                raise interfaces.InvalidValue(None, self._model)
            self._content = pack(self._model, definition, self._bundle)
            type_definition = REGISTRY.type_for_definition(definition)
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
            if self.fhir_link is None:
                self.fhir_link = self._bundle.link_generator(
                    self._model, self.resource_type)

        entry = {
            "id": utils.strip_history_from_link(self.fhir_link),
            "links": [{"rel": "self",
                       "url": self.fhir_link}],
            "content": self._content
        }
        return entry

    def __eq__(self, other):
        if isinstance(other, dict):
            return other.get('reference', None) in (
                self.fhir_link, self.fhir_unversioned_link)
        return NotImplemented()

    def __format__(self, _):
        return '<BundleEntry fhir_link="{}" type="{}">{}</BundleEntry>'.format(
            self.fhir_link,
            self.resource_type,
            json.dumps(self._content, indent=2, sort_keys=True))


class Bundle(object):

    def __init__(self, domain=None, link_generator=None):
        self.items = []
        self.domain = domain
        self.link_generator = link_generator

    def add_payload(self, response):
        if response['resourceType'] != 'Bundle':
            raise interfaces.InvalidBundle(response)
        for entry in response['entry']:
            bundle_entry = BundleEntry(self, entry=entry)
            print '{}'.format(bundle_entry)
            self.items.append(bundle_entry)

    def add_model(self, model):
        bundle_entry = BundleEntry(self, model=model)
        self.items.append(bundle_entry)

    def find(self, reference):
        for item in self.items:
            if reference == item:
                return item
        return None

    def pack(self):
        for item in self.items:
            try:
                yield item.pack()
            except:
                import pdb; pdb.post_mortem()

    def get_payload(self):
        entries = list(self.pack())
        now = datetime.datetime.utcnow()
        return {
            "resourceType": "Bundle",
            "id": "urn:uuid:{}".format(uuid.uuid4()),
            "updated": "{}Z".format(now.isoformat()),
            "entry": entries
        }

    def unpack(self):
        for item in self.items:
            yield item.unpack()
