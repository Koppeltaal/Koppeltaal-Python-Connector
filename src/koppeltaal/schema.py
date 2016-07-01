import koppeltaal.interfaces
import koppeltaal.codes


class Value(object):

    def __init__(
            self,
            name,
            value_type,
            optional=False,
            multiple=False,
            binding=None,
            extension=None):
        self.value_type = value_type
        self.name = name
        self.binding = binding
        self.optional = optional
        self.multiple = multiple
        self.extension = extension


class ActivityDefinitionSchema(object):

    identifier = Value(
        'identifier', 'string',
        extension='ActivityDefinition#ActivityDefinitionIdentifier')

    kind = Value(
        'type', 'code',
        binding=koppeltaal.codes.ACTIVITY_KIND,
        extension='ActivityDefinition#ActivityKind')

    name = Value(
        'name', 'string',
        extension='ActivityDefinition#ActivityName')

    description = Value(
        'description', 'string',
        optional=True,
        extension='ActivityDefinition#ActivityDescription')

    performer = Value(
        'defaultPerformer', 'code',
        optional=True,
        extension='ActivityDefinition#DefaultPerformer')

    is_active = Value(
        'isActive', 'boolean',
        optional=True,
        extension='ActivityDefinition#IsActive')

    is_domain_specific = Value(
        'isDomainSpecific', 'boolean',
        optional=True,
        extension='ActivityDefinition#IsDomainSpecific')

    is_archived = Value(
        'isArchived', 'boolean',
        optional=True,
        extension='ActivityDefinition#IsArchived')


class MessageHeaderSchema(object):

    timestamp = Value(
        'timestamp', 'instant')

    data = Value(
        'data', 'reference',
        optional=True)

    patient = Value(
        'data', 'reference',
        extension='MessageHeader#Patient')

    event = Value(
        'event', 'code',
        binding=koppeltaal.codes.MESSAGE_EVENTS)
