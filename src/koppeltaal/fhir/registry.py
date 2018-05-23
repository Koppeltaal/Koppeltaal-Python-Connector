# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import zope.interface

from koppeltaal import definitions


def _inspect_definition(fields, definition):
    for name, field in definition.namesAndDescriptions():
        if not isinstance(field, definitions.Field):
            continue
        if field.extension:
            continue
        if field.multiple:
            fields.add(field.name)
        if field.field_type == 'object':
            _inspect_definition(fields, field.binding)


class Registry(dict):

    def repeatable_field_names(self, fhir_type):
        fields = {'extension', 'coding'}
        if fhir_type == 'Other':
            return fields

        for definition in self.keys():
            defined_type = definition.queryTaggedValue('resource type')
            if not defined_type:
                continue
            if defined_type[0] != fhir_type:
                continue
            _inspect_definition(fields, definition)

        return fields

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
