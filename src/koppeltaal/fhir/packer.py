# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import datetime
import dateutil.parser
import six
import zope.interface

from koppeltaal import (
    fhir,
    compat,
    definitions,
    interfaces,
    models,
    utils)


basestring = six.string_types
unicode = six.text_type


@zope.interface.implementer(interfaces.IBrokenFHIRResource)
class BrokenResource(object):
    fhir_link = None
    error = None
    payload = None

    def __init__(self, error, payload):
        self.error = error
        self.payload = payload

    def __str__(self):
        return u"Broken resource '{}': {}".format(self.fhir_link, self.error)


class Extension(object):

    def __init__(self, packer, content=None):
        self._packer = packer
        self._index = {}
        if content and 'extension' in content:
            for extension in content['extension']:
                url = extension['url']
                self._index.setdefault(url, []).append(extension)
        compat.extensions(self._index)

    def _unpack_item(self, field, extension):
        if field.field_type == 'boolean':
            value = extension.get('valueBoolean')
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, extension)
            return value

        if field.field_type == 'codeable':
            # Note how 'codeable' is actually an extension data type but we
            # treat it specially here.
            value = extension.get('valueCodeableConcept')
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, extension)
            if 'coding' not in value:
                raise interfaces.InvalidValue(field, extension)
            if not isinstance(value['coding'], list):
                raise interfaces.InvalidValue(field, extension)
            if len(value['coding']) != 1:
                raise interfaces.InvalidValue(field, extension)
            return field.binding.unpack_coding(value['coding'][0])

        if field.field_type == 'code':
            value = extension.get('valueCode')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, extension)
            return field.binding.unpack_code(value)

        if field.field_type == 'coding':
            # Note how 'coding' is actually an extension data type but we
            # treat it specially here.
            value = extension.get('valueCoding')
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, extension)
            return field.binding.unpack_coding(value)

        if field.field_type == 'date':
            value = extension.get('valueDate')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, extension)
            try:
                return dateutil.parser.parse(value).date()
            except ValueError:
                raise interfaces.InvalidValue(field, extension)

        if field.field_type == 'datetime':
            value = extension.get('valueDateTime')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, extension)
            try:
                return dateutil.parser.parse(value)
            except ValueError:
                raise interfaces.InvalidValue(field, extension)

        if field.field_type == 'instant':
            value = extension.get('valueInstant')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, extension)
            try:
                return dateutil.parser.parse(value)
            except ValueError:
                raise interfaces.InvalidValue(field, extension)

        if field.field_type == 'integer':
            value = extension.get('valueInteger')
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, extension)
            return value

        if field.field_type == 'object':
            key = field.binding.queryTaggedValue('extension data type')
            if key is None:
                value = extension.get('extension')
                if not isinstance(value, list):
                    raise interfaces.InvalidValue(field, extension)
                return self._packer.unpack(extension, field.binding)

            value = extension.get(key)
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, extension)
            return self._packer.unpack(value, field.binding)

        if field.field_type in {'reference', 'versioned reference'}:
            value = extension.get('valueResource')
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, extension)
            return self._packer.unpack_reference(value)

        if field.field_type == 'string':
            value = extension.get('valueString')
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, extension)
            return value

        raise NotImplementedError()

    def unpack(self, field):
        if field.url not in self._index:
            if field.optional:
                if field.multiple:
                    return []
                return field.default
            raise interfaces.RequiredMissing(field)
        extensions = self._index[field.url]
        if field.multiple:
            values = []
            for extension in extensions:
                values.append(self._unpack_item(field, extension))
            return values

        if len(extensions) != 1:
            raise interfaces.InvalidValue(field)
        return self._unpack_item(field, extensions[0])

    @property
    def payload(self):
        all_extensions = []
        for extensions in self._index.values():
            all_extensions.extend(extensions)
        if all_extensions:
            return {"extension": all_extensions}
        return {}

    def _pack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return {'valueBoolean': value}

        if field.field_type == 'code':
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return {'valueCode': field.binding.pack_code(value)}

        if field.field_type == 'codeable':
            # Note how 'codeable' is actually an extension data type but we
            # treat it specially here.
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return {"valueCodeableConcept":
                    {"coding": [field.binding.pack_coding(value)]}}

        if field.field_type == 'coding':
            # Note how 'coding' is actually an extension data type but we
            # treat it specially here.
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
                # We need a timezone! We assume timezone-naive datetimes
                # represent UTC times. So we add the UTC tzinfo here.
                value = value.replace(tzinfo=utils.utc, microsecond=0)
            return {'valueInstant': value.isoformat()}

        if field.field_type == 'integer':
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return {'valueInteger': value}

        if field.field_type == 'object':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            key = field.binding.queryTaggedValue('extension data type')
            if key is None:
                return self._packer.pack(value, field.binding)
            return {key: self._packer.pack(value, field.binding)}

        if field.field_type == 'reference':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            return {'valueResource': self._packer.pack_reference(value)}

        if field.field_type == 'versioned reference':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            ref = self._packer.pack_reference(value, versioned=True)
            return {'valueResource': ref}

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return {'valueString': value}

        raise NotImplementedError()

    def pack(self, field, value):
        if field.is_empty(value):
            if not field.optional:
                raise interfaces.InvalidValue(field, value)
            return
        if field.multiple:
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
        else:
            value = [value]
        for single_value in value:
            extension = {"url": field.url}
            extension.update(self._pack_item(field, single_value))
            self._index.setdefault(field.url, []).append(extension)


class Native(object):

    def __init__(self, packer, content=None):
        self._packer = packer
        self._content = content or {}

    @property
    def payload(self):
        return self._content.copy()

    def _unpack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'codeable':
            # Note how 'codeable' is actually an extension data type but we
            # treat it specially here.
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
            # Note how 'coding' is actually an extension data type but we
            # treat it specially here.
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            return field.binding.unpack_coding(value)

        if field.field_type == 'date':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            try:
                return dateutil.parser.parse(value).date()
            except ValueError:
                raise interfaces.InvalidValue(field, value)

        if field.field_type == 'datetime':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            try:
                return dateutil.parser.parse(value)
            except ValueError:
                raise interfaces.InvalidValue(field, value)

        if field.field_type == 'instant':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            try:
                return dateutil.parser.parse(value)
            except ValueError:
                raise interfaces.InvalidValue(field, value)

        if field.field_type == 'integer':
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'object':
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            return self._packer.unpack(value, field.binding)

        if field.field_type in {'reference', 'versioned reference'}:
            if not isinstance(value, dict):
                raise interfaces.InvalidValue(field, value)
            return self._packer.unpack_reference(value)

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def unpack(self, field):
        if field.name not in self._content:
            if field.optional:
                if field.multiple:
                    return []
                return field.default
            raise interfaces.RequiredMissing(field)

        value = self._content[field.name]
        if field.multiple:
            # If the field is multiple there is a list of item. We
            # only support the first one at the moment.
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
            if not len(value):
                raise interfaces.RequiredMissing(field)
            if field.multiple:
                return [self._unpack_item(field, v) for v in value]
            value = value[0]
        return self._unpack_item(field, value)

    def _pack_item(self, field, value):
        if field.field_type == 'boolean':
            if not isinstance(value, bool):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'codeable':
            # Note how 'codeable' is actually an extension data type but we
            # treat it specially here.
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return {"coding": [field.binding.pack_coding(value)]}

        if field.field_type == 'code':
            if not isinstance(value, basestring):
                raise interfaces.InvalidValue(field, value)
            return field.binding.pack_code(value)

        if field.field_type == 'coding':
            # Note how 'coding' is actually an extension data type but we
            # treat it specially here.
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
                value = value.replace(tzinfo=utils.utc, microsecond=0)
            return value.isoformat()

        if field.field_type == 'integer':
            if not isinstance(value, int):
                raise interfaces.InvalidValue(field, value)
            return value

        if field.field_type == 'object':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            return self._packer.pack(value, field.binding)

        if field.field_type == 'reference':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            return self._packer.pack_reference(value)

        if field.field_type == 'versioned reference':
            if not isinstance(value, object):
                raise interfaces.InvalidValue(field, value)
            return self._packer.pack_reference(value, versioned=True)

        if field.field_type == 'string':
            if not isinstance(value, unicode):
                raise interfaces.InvalidValue(field, value)
            return value

        raise NotImplementedError()

    def pack(self, field, value):
        if field.is_empty(value):
            if not field.optional:
                raise interfaces.InvalidValue(field, value)
            return
        if field.multiple:
            if not isinstance(value, list):
                raise interfaces.InvalidValue(field, value)
            item = [self._pack_item(field, v) for v in value]
        else:
            assert field.multiple is False
            item = self._pack_item(field, value)
        self._content[field.name] = item


class Packer(object):

    def __init__(self, resource, fhir_link):
        self.resource = resource
        self.fhir_link = fhir_link
        self._idref = 0

    def idref(self):
        self._idref += 1
        return 'ref{0:03}'.format(self._idref)

    def unpack(self, payload, definition, allow_broken=False):
        factory = fhir.REGISTRY.model_for_definition(definition)
        if factory is None:
            return None

        try:
            extension = Extension(self, payload)
            native = Native(self, payload)
            data = {}
            for name, field in definition.namesAndDescriptions():
                if not isinstance(field, definitions.Field):
                    continue
                if field.extension is None:
                    data[name] = native.unpack(field)
                else:
                    data[name] = extension.unpack(field)
            return factory(**data)
        except interfaces.InvalidValue as error:
            if allow_broken:
                return BrokenResource(error, payload)
            raise

    def pack(self, model, definition):
        extension = Extension(self)
        native = Native(self)

        if not definition.providedBy(model):
            raise interfaces.InvalidResource(definition, model)

        for name, field in definition.namesAndDescriptions():
            if not isinstance(field, definitions.Field):
                continue
            value = getattr(model, name, field.default)
            if field.extension is None:
                native.pack(field, value)
            else:
                extension.pack(field, value)
        # We do not have to add an idref because we do not refer back to
        # any object. However due to a bug the Javascript connector
        # requires it in some cases.
        payload = {'id': self.idref()}
        payload.update(extension.payload)
        payload.update(native.payload)
        return payload

    def unpack_reference(self, value):
        reference = self.resource.find(value)
        if reference:
            return reference.unpack()
        if not ('reference' in value or 'display' in value):
            raise interfaces.InvalidReference(value)
        return models.ReferredResource(
            fhir_link=value.get('reference'),
            display=value.get('display'))

    def pack_reference(self, value, versioned=False):
        if interfaces.IReferredFHIRResource.providedBy(value):
            reference = {}
            if value.fhir_link:
                reference['reference'] = value.fhir_link
            if value.display:
                reference['display'] = value.display
            if not reference:
                raise interfaces.InvalidReference(value)
            return reference
        entry = self.resource.add_model(value)
        ref = entry.fhir_link
        if not versioned:
            ref = utils.strip_history_from_link(ref)
        return {'reference': ref}
