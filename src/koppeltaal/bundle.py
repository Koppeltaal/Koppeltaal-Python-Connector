import json
import dateutil.parser
import koppeltaal.interfaces
import koppeltaal.definitions
import koppeltaal.models
import koppeltaal.utils

MARKER = object()

TYPES = {
    'ActivityDefinition': koppeltaal.definitions.ActivityDefinition,
    'MessageHeader': koppeltaal.definitions.MessageHeader,
}

FACTORIES = {
    koppeltaal.definitions.ActivityDefinition: koppeltaal.models.Activity,
    koppeltaal.definitions.MessageHeader: koppeltaal.models.Message,
    koppeltaal.definitions.ProcessingStatus: koppeltaal.models.Status,
    koppeltaal.definitions.Source: koppeltaal.models.Source,
    koppeltaal.definitions.SubActivity: koppeltaal.models.SubActivity,
}


class Extension(object):

    def __init__(self, content, bundle):
        self._bundle = bundle
        self._index = {}
        if 'extension' in content:
            for extension in content['extension']:
                url = extension['url']
                self._index.setdefault(url, []).append(extension)

    def _unpack_item(self, field, extension):
        if field.field_type == 'boolean':
            value = extension.get('valueBoolean')
            if not isinstance(value, bool):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'code':
            value = extension.get('valueCode')
            if not isinstance(value, unicode):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            if field.binding and value not in field.binding:
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'coding':
            value = extension.get('valueCoding')
            if not isinstance(value, dict):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return field.binding.unpack(value)

        if field.field_type == 'instant':
            value = extension.get('valueInstant')
            if not isinstance(value, unicode):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

        if field.field_type == 'object':
            value = extension.get('extension')
            if not isinstance(value, list):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return unpack(extension, field.binding, self._bundle)

        if field.field_type == 'reference':
            value = extension.get('valueResource')
            if not isinstance(value, dict):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            reference = self._bundle.find(value)
            if reference:
                return reference.unpack()
            return None

        if field.field_type == 'string':
            value = extension.get('valueString')
            if not isinstance(value, unicode):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def unpack(self, field):
        if field.url not in self._index:
            if field.optional:
                return None
            raise koppeltaal.interfaces.RequiredMissing(field)
        extensions = self._index[field.url]
        if field.multiple is koppeltaal.definitions.ALL_ITEMS:
            values = []
            for extension in extensions:
                values.append(self._unpack_item(field, extension))
            return values

        if not field.multiple and len(extensions) != 1:
            raise koppeltaal.interfaces.InvalidValue(field)
        return self._unpack_item(field, extensions[0])


class Native(object):

    def __init__(self, content, bundle):
        self._bundle = bundle
        self._content = content

    def _unpack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'code':
            if not isinstance(value, unicode):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'coding':
            if not isinstance(value, dict):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return field.binding.unpack(value)

        if field.field_type == 'instant':
            if not isinstance(value, unicode):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return dateutil.parser.parse(value)

        if field.field_type == 'object':
            if not isinstance(value, dict):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return unpack(value, field.binding, self._bundle)

        if field.field_type == 'reference':
            if not isinstance(value, dict):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            reference = self._bundle.find(value)
            if reference is not None:
                return reference.unpack()
            return None

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def unpack(self, field):
        if field.name not in self._content:
            if field.optional:
                return None
            raise koppeltaal.interfaces.RequiredMissing(field)

        value = self._content[field.name]
        if field.multiple:
            # If the field is multiple there is a list of item. We
            # only support the first one at the moment.
            if not isinstance(value, list):
                raise koppeltaal.interfaces.InvalidValue(field, value)
            if not len(value):
                if field.optional:
                    return None
                raise koppeltaal.interfaces.RequiredMissing(field)
            if field.multiple is koppeltaal.definitions.ALL_ITEMS:
                return [self._unpack_value(field, v) for v in value]
            value = value[0]
        return self._unpack_value(field, value)


def unpack(item, definition, bundle):
    factory = FACTORIES.get(definition)
    if factory is None:
        return None
    model = factory()

    extension = Extension(item, bundle)
    native = Native(item, bundle)
    for name in dir(definition):
        field = getattr(definition, name)
        if not isinstance(field, koppeltaal.definitions.Field):
            continue
        if field.extension is None:
            setattr(model, name, native.unpack(field))
        else:
            setattr(model, name, extension.unpack(field))
    return model


class BundleItem(object):
    unpacked_item = MARKER

    def __init__(self, bundle, entry):
        self._bundle = bundle
        self.uids = filter(
            None,
            [entry['id'], koppeltaal.utils.json2links(entry).get('self')])
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
        if self.unpacked_item is MARKER:
            definition = TYPES.get(self.resource_type)
            if definition is None:
                self.unpacked_item = None
            model = unpack(self._content, definition, self._bundle)
            model.uid = self.uid
            self.unpacked_item = model
        return self.unpacked_item

    def __eq__(self, other):
        if isinstance(other, dict):
            return other.get('reference', None) in self.uids
        return NotImplemented()

    def __format__(self, _):
        return '<BundleItem uids="{}" type="{}">{}</BundleItem>'.format(
            ', '.join(self.uids),
            self.resource_type,
            json.dumps(self._content, indent=2, sort_keys=True))


class Bundle(object):

    def __init__(self):
        self.items = []

    def add(self, entry):
        item = BundleItem(self, entry)
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
