import koppeltaal.interfaces
import koppeltaal.codes


FIELD_TYPES = {
    'boolean',
    'code',
    'coding',
    'instant',
    'object',
    'reference',
    'string',
}
ALL_ITEMS = object()
FIRST_ITEM = object()


class Field(object):

    def __init__(
            self,
            name,
            field_type,
            optional=False,
            multiple=False,
            binding=None,
            extension=None):
        assert field_type in FIELD_TYPES, \
            'Unknown field type {} for {}.'.format(field_type, name)
        assert field_type not in {'object', 'coding'} or binding, \
            'Missing binding for {}.'.format(name)
        self.field_type = field_type
        self.name = name
        self.binding = binding
        self.optional = optional
        self.multiple = multiple
        self.extension = extension
        self.url = None
        if extension:
            self.url = koppeltaal.interfaces.NAMESPACE + extension


class SubActivity(object):

    name = Field(
        'name', 'string',
        extension='ActivityDefinition#SubActivityName')

    identifier = Field(
        'identifier', 'string',
        extension='ActivityDefinition#SubActivityIdentifier')

    description = Field(
        'identifier', 'string',
        optional=True,
        extension='ActivityDefinition#SubActivityDescription')

    active = Field(
        'isActive', 'boolean',
        optional=True,
        extension='ActivityDefinition#SubActivityIsActive')


class ActivityDefinition(object):

    identifier = Field(
        'identifier', 'string',
        extension='ActivityDefinition#ActivityDefinitionIdentifier')

    kind = Field(
        'type', 'coding',
        binding=koppeltaal.codes.ACTIVITY_KIND,
        extension='ActivityDefinition#ActivityKind')

    name = Field(
        'name', 'string',
        extension='ActivityDefinition#ActivityName')

    description = Field(
        'description', 'string',
        optional=True,
        extension='ActivityDefinition#ActivityDescription')

    subactivities = Field(
        'subActivity', 'object',
        optional=True,
        multiple=ALL_ITEMS,
        binding=SubActivity,
        extension='ActivityDefinition#SubActivity')

    performer = Field(
        'defaultPerformer', 'coding',
        optional=True,
        binding=koppeltaal.codes.ACTIVITY_PERFORMER,
        extension='ActivityDefinition#DefaultPerformer')

    is_active = Field(
        'isActive', 'boolean',
        optional=True,
        extension='ActivityDefinition#IsActive')

    is_domain_specific = Field(
        'isDomainSpecific', 'boolean',
        optional=True,
        extension='ActivityDefinition#IsDomainSpecific')

    is_archived = Field(
        'isArchived', 'boolean',
        optional=True,
        extension='ActivityDefinition#IsArchived')


class ProcessingStatus(object):

    status = Field(
        'status', 'code',
        optional=True,
        binding=koppeltaal.codes.PROCESSING_STATUS,
        extension='MessageHeader#ProcessingStatusStatus')

    last_changed = Field(
        'statusLastChanged', 'instant',
        extension='MessageHeader#ProcessingStatusStatusLastChanged')

    exception = Field(
        'exception', 'string',
        optional=True,
        extension='MessageHeader#ProcessingStatusException')


class Source(object):

    name = Field(
        'name', 'string',
        optional=True)

    software = Field(
        'software', 'string')

    version = Field(
        'version', 'string',
        optional=True)

    endpoint = Field(
        'endpoint', 'string')


class MessageHeader(object):

    timestamp = Field(
        'timestamp', 'instant')

    data = Field(
        'data', 'reference',
        multiple=FIRST_ITEM,
        optional=True)

    patient = Field(
        'patient', 'reference',
        extension='MessageHeader#Patient')

    event = Field(
        'event', 'coding',
        binding=koppeltaal.codes.MESSAGE_EVENTS)

    status = Field(
        'processingStatus', 'object',
        optional=True,
        binding=ProcessingStatus,
        extension='MessageHeader#ProcessingStatus')

    source = Field(
        'source', 'object',
        binding=Source)
