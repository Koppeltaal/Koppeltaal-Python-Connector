import zope.interface
import koppeltaal.interfaces
import koppeltaal.codes


FIELD_TYPES = {
    'boolean',
    'codable',
    'code',
    'coding',
    'date',
    'datetime',
    'instant',
    'integer',
    'object',
    'reference',
    'string',
}
RESERVED_NAMES = {
    'extension',
    'id',
    'language',
    'resourceType',
    'text',
}
ALL_ITEMS = object()
FIRST_ITEM = object()


class Field(zope.interface.Attribute):

    def __init__(
            self,
            name,
            field_type,
            optional=False,
            multiple=False,
            binding=None,
            extension=None):
        super(Field, self).__init__(__name__='')
        assert name not in RESERVED_NAMES, '{} is a reserved name.'
        assert field_type in FIELD_TYPES, \
            'Unknown field type {} for {}.'.format(field_type, name)
        assert field_type not in {
            'object', 'codeable', 'code', 'coding'} or binding, \
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


def resource_type(name, non_standard=False):

    def resource_iface(cls):
        assert issubclass(cls, FHIRResource)
        cls.setTaggedValue('resource type', (name, non_standard))
        return cls

    return resource_iface


class FHIRResource(zope.interface.Interface):
    fhir_link = zope.interface.Attribute(
        'Link to resource containing resource type, id and version')


class SubActivityDefinition(zope.interface.Interface):

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


@resource_type('ActivityDefinition', True)
class ActivityDefinition(FHIRResource):

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
        binding=SubActivityDefinition,
        extension='ActivityDefinition#SubActivity')

    performer = Field(
        'defaultPerformer', 'coding',
        optional=True,
        binding=koppeltaal.codes.ACTIVITY_PERFORMER,
        extension='ActivityDefinition#DefaultPerformer')

    launch_type = Field(
        'launchType', 'code',
        optional=True,
        binding=koppeltaal.codes.ACTIVITY_LAUNCH_TYPE,
        extension='ActivityDefinition#LaunchType')

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


class Name(zope.interface.Interface):

    given = Field(
        'given', 'string',
        optional=True,
        multiple=FIRST_ITEM)

    family = Field(
        'family', 'string',
        optional=True,
        multiple=FIRST_ITEM)

    use = Field(
        'use', 'code',
        binding=koppeltaal.codes.NAME_USE)


@resource_type('Patient')
class Patient(FHIRResource):

    name = Field(
        'name', 'object',
        binding=Name,
        multiple=FIRST_ITEM)

    age = Field(
        'age', 'integer',
        optional=True,
        binding='Patient#Age')

    birth_date = Field(
        'birthDate', 'datetime',
        optional=True)


@resource_type('Practitioner')
class Practitioner(FHIRResource):

    name = Field(
        'name', 'object',
        binding=Name)


class Participant(zope.interface.Interface):

    member = Field(
        'member', 'reference')

    role = Field(
        'role', 'codable',
        optional=True,
        binding=koppeltaal.codes.CAREPLAN_PARTICIPANT_ROLE)


class Goal(zope.interface.Interface):

    description = Field(
        'description', 'string')

    status = Field(
        'status', 'code',
        binding=koppeltaal.codes.CAREPLAN_GOAL_STATUS)

    notes = Field(
        'notes', 'string',
        optional=True)


class SubActivity(zope.interface.Interface):

    # Note how this definition "points" to the `identifier` one of the
    # `ActivityDefinition.subActivity`.
    definition = Field(
        'identifier', 'string',
        extension='CarePlan#SubActivityIdentifier')

    status = Field(
        'status', 'code',
        binding=koppeltaal.codes.CAREPLAN_ACTIVITY_STATUS,
        optional=True,
        extension='CarePlan#SubActivityStatus')


class Activity(zope.interface.Interface):

    identifier = Field(
        'identifier', 'string',
        optional=True,
        extension='CarePlan#ActivityIdentifier')

    cancelled = Field(
        'cancelled', 'instant',
        optional=True,
        extension='CarePlan#Cancelled')

    # Note how this definition "points" to the `identifier` one of the
    # `ActivityDefinition`.
    definition = Field(
        'definition', 'string',
        optional=True,
        extension='CarePlan#ActivityDefinition')

    description = Field(
        'description', 'string',
        optional=True,
        extension='CarePlan#ActivityDescription')

    finished = Field(
        'finished', 'instant',
        optional=True,
        extension='CarePlan#Finished')

    # Note the `kind` should match the `kind` of the `ActivityDefinition`
    # we're pointing to.
    kind = Field(
        'type', 'coding',
        binding=koppeltaal.codes.ACTIVITY_KIND,
        extension='CarePlan#ActivityKind')

    notes = Field(
        'notes', 'string',
        optional=True)

    participants = Field(
        'participant', 'object',
        binding=Participant,
        optional=True,
        multiple=ALL_ITEMS,
        extension='CarePlan#Participant')

    planned = Field(
        'startDate', 'datetime',
        optional=True,
        extension='CarePlan#StartDate')

    started = Field(
        'started', 'instant',
        optional=True,
        extension='CarePlan#Started')

    # This is the older version of the `status`. KT 1.1.1 uses a `code` and
    # points to the http://hl7.org/fhir/care-plan-activity-status value set.
    # Perhaps we can update it and still be compatible with Kickass Game and
    # more importantly, with KT 1.1.1.
    status = Field(
        'status', 'coding',
        binding=koppeltaal.codes.CAREPLAN_ACTIVITY_STATUS,
        extension='CarePlan#ActivityStatus')

    subactivities = Field(
        'subactivity', 'object',
        binding=SubActivity,
        optional=True,
        multiple=ALL_ITEMS,
        extension='CarePlan#SubActivity')


@resource_type('CarePlan')
class CarePlan(FHIRResource):

    activities = Field(
        'activity', 'object',
        binding=Activity,
        optional=True,
        multiple=ALL_ITEMS)

    participants = Field(
        'participant', 'object',
        binding=Participant,
        optional=True,
        multiple=ALL_ITEMS)

    patient = Field(
        'patient', 'reference')

    status = Field(
        'status', 'code',
        binding=koppeltaal.codes.CAREPLAN_STATUS)

    goals = Field(
        'goal', 'object',
        binding=Goal,
        optional=True,
        multiple=ALL_ITEMS)


class ProcessingStatus(zope.interface.Interface):

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


class Source(zope.interface.Interface):

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


@resource_type('MessageHeader')
class MessageHeader(FHIRResource):

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
