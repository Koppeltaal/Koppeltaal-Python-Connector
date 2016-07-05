import json
import dateutil.parser
import datetime

from koppeltaal import (
    interfaces,
    definitions,
    models,
    utils)


MARKER = object()

TYPES = {
    'ActivityDefinition': definitions.ActivityDefinition,
    'CarePlan': definitions.CarePlan,
    'MessageHeader': definitions.MessageHeader,
    'Patient': definitions.Patient,
    'Practitioner': definitions.Practitioner,
}

FACTORIES = {
    definitions.Activity: models.Activity,
    definitions.ActivityDefinition: models.ActivityDefinition,
    definitions.CarePlan: models.CarePlan,
    definitions.Goal: models.Goal,
    definitions.MessageHeader: models.Message,
    definitions.Name: models.Name,
    definitions.Participant: models.Participant,
    definitions.Patient: models.Patient,
    definitions.Practitioner: models.Practitioner,
    definitions.ProcessingStatus: models.Status,
    definitions.Source: models.Source,
    definitions.SubActivity: models.SubActivity,
    definitions.SubActivityDefinition: models.SubActivityDefinition,
}


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

        if field.field_type == 'instant':
            value = extension.get('valueInstant')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

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

        if field.field_type == 'instant':
            if not isinstance(value, datetime.datetime):
                raise interfaces.InvalidValue(field, value)
            if value.tzinfo is None:
                # We need a timezone!
                # XXX maybe automatically add UTC.
                raise interfaces.InvalidValue(field, value)
            return {'valueInstant': value.isoformat()}

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
        extension = {"url": field.url}
        extension.update(self._pack_item(field, value))
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

        if field.field_type == 'instant':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

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

        if field.field_type == 'instant':
            if not isinstance(value, datetime.datetime):
                raise interfaces.InvalidValue(field, value)
            if value.tzinfo is None:
                # We need a timezone!
                # XXX maybe automatically add UTC.
                raise interfaces.InvalidValue(field, value)
            return value.isoformat()

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
    factory = FACTORIES.get(definition)
    if factory is None:
        return None
    model = factory()

    extension = Extension(bundle, item)
    native = Native(bundle, item)
    for name in dir(definition):
        field = getattr(definition, name)
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

    for name in dir(definition):
        field = getattr(definition, name)
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
    _item = MARKER

    def __init__(self, bundle, entry):
        self._bundle = bundle
        self.uids = filter(
            None,
            [entry['id'], utils.json2links(entry).get('self')])
        self._content = entry['content'].copy()
        resource_type = self._content.pop('resourceType', 'Other')
        if resource_type == 'Other':
            assert 'code' in self._content
            for code in self._content.pop('code').get('coding', []):
                resource_type = code.get('code', 'Other')
        assert resource_type != 'Other'
        self.resource_type = resource_type

    @property
    def uid(self):
        return self.uids[0]

    def unpack(self):
        if self._item is not MARKER:
            return self._item

        self._item = None
        definition = TYPES.get(self.resource_type)
        if definition is not None:
            self._item = unpack(self._content, definition, self._bundle)
            if self._item is not None:
                self._item.uid = self.uid
        return self._item

    def __eq__(self, other):
        if isinstance(other, dict):
            return other.get('reference', None) in self.uids
        return NotImplemented()

    def __format__(self, _):
        return '<BundleEntry uids="{}" type="{}">{}</BundleEntry>'.format(
            ', '.join(self.uids),
            self.resource_type,
            json.dumps(self._content, indent=2, sort_keys=True))


class Bundle(object):

    def __init__(self):
        self.items = []

    def add_response(self, response):
        if response['resourceType'] != 'Bundle':
            raise interfaces.InvalidBundle(response)
        for entry in response['entry']:
            item = BundleEntry(self, entry)
            print '{}'.format(item)
            self.items.append(item)

    def find(self, reference):
        for item in self.items:
            if reference == item:
                return item
        return None

    def unpack(self):
        for item in self.items:
            try:
                yield item.unpack()
            except:
                import pdb; pdb.post_mortem()
