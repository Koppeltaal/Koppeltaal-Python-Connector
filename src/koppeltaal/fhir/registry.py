
import zope.interface


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
