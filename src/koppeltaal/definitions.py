import zope.interface

from koppeltaal import (interfaces, codes)


FIELD_TYPES = {
    'boolean',
    'codeable',
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
            default=None,
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
        self.default = default
        self.optional = optional
        self.multiple = multiple
        self.extension = extension
        self.url = None
        if extension:
            self.url = interfaces.NAMESPACE + extension


def resource_type(name, standard=True):

    def resource_iface(cls):
        assert issubclass(cls, interfaces.IFHIRResource)
        cls.setTaggedValue('resource type', (name, standard))
        return cls

    return resource_iface


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


@resource_type('ActivityDefinition', False)
class ActivityDefinition(interfaces.IIdentifiedFHIRResource):

    application = Field(
        'application', 'reference',
        extension='ActivityDefinition#Application')

    identifier = Field(
        'identifier', 'string',
        extension='ActivityDefinition#ActivityDefinitionIdentifier')

    kind = Field(
        'type', 'coding',
        binding=codes.ACTIVITY_KIND,
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
        binding=codes.ACTIVITY_PERFORMER,
        extension='ActivityDefinition#DefaultPerformer')

    launch_type = Field(
        'launchType', 'code',
        optional=True,
        binding=codes.ACTIVITY_LAUNCH_TYPE,
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


class CarePlanSubActivityStatus(zope.interface.Interface):

    definition = Field(
        'identifier', 'string',
        extension='CarePlanActivityStatus#SubActivityIdentifier')

    status = Field(
        'status', 'coding',
        binding=codes.CAREPLAN_ACTIVITY_STATUS,
        extension='CarePlanActivityStatus#SubActivityStatus')


@resource_type('CarePlanActivityStatus', False)
class CarePlanActivityStatus(interfaces.IIdentifiedFHIRResource):

    identifier = Field(
        'activity', 'string',
        extension='CarePlanActivityStatus#Activity')

    status = Field(
        'activityStatus', 'coding',
        binding=codes.CAREPLAN_ACTIVITY_STATUS,
        extension='CarePlanActivityStatus#ActivityStatus')

    subactivities = Field(
        'subactivity', 'object',
        binding=CarePlanSubActivityStatus,
        extension='CarePlanActivityStatus#SubActivity',
        multiple=ALL_ITEMS,
        optional=True)

    percentage = Field(
        'percentageCompleted', 'integer',
        optional=True,
        extension='CarePlanActivityStatus#PercentageCompleted')


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
        optional=True,
        binding=codes.NAME_USE)


class Contact(zope.interface.Interface):

    system = Field(
        'system', 'code',
        optional=True,
        binding=codes.CONTACT_SYSTEM)

    value = Field(
        'value', 'string',
        optional=True)

    use = Field(
        'use', 'code',
        optional=True,
        binding=codes.CONTACT_USE)


class Identifier(zope.interface.Interface):

    system = Field(
        'system', 'string',
        optional=True)

    value = Field(
        'value', 'string',
        optional=True)

    use = Field(
        'use', 'code',
        optional=True,
        binding=codes.IDENTIFIER_USE)


@resource_type('Patient')
class Patient(interfaces.IIdentifiedFHIRResource):

    active = Field(
        'active', 'boolean',
        optional=True)

    age = Field(
        'age', 'integer',
        optional=True,
        extension='Patient#Age')

    birth_date = Field(
        'birthDate', 'datetime',
        optional=True)

    contacts = Field(
        'telecom', 'object',
        binding=Contact,
        multiple=ALL_ITEMS,
        optional=True)

    identifiers = Field(
        'identifier', 'object',
        binding=Identifier,
        multiple=ALL_ITEMS,
        optional=True)

    gender = Field(
        'gender', 'codeable',
        binding=codes.GENDER,
        optional=True)

    name = Field(
        'name', 'object',
        binding=Name,
        multiple=FIRST_ITEM)


@resource_type('Practitioner')
class Practitioner(interfaces.IIdentifiedFHIRResource):

    contacts = Field(
        'telecom', 'object',
        binding=Contact,
        multiple=ALL_ITEMS,
        optional=True)

    identifiers = Field(
        'identifier', 'object',
        binding=Identifier,
        multiple=ALL_ITEMS,
        optional=True)

    name = Field(
        'name', 'object',
        binding=Name)


class Participant(zope.interface.Interface):

    member = Field(
        'member', 'reference')

    role = Field(
        'role', 'codeable',
        optional=True,
        binding=codes.CAREPLAN_PARTICIPANT_ROLE)


class Goal(zope.interface.Interface):

    description = Field(
        'description', 'string')

    status = Field(
        'status', 'code',
        binding=codes.CAREPLAN_GOAL_STATUS)

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
        binding=codes.CAREPLAN_ACTIVITY_STATUS,
        optional=True,
        extension='CarePlan#SubActivityStatus')


class ActivityParticipant(zope.interface.Interface):

    member = Field(
        'member', 'reference',
        extension='CarePlan#ParticipantMember')

    role = Field(
        'role', 'codeable',
        optional=True,
        binding=codes.CAREPLAN_PARTICIPANT_ROLE,
        extension='CarePlan#ParticipantRole')


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
        binding=codes.ACTIVITY_KIND,
        extension='CarePlan#ActivityKind')

    notes = Field(
        'notes', 'string',
        optional=True)

    participants = Field(
        'participant', 'object',
        binding=ActivityParticipant,
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
        binding=codes.CAREPLAN_ACTIVITY_STATUS,
        extension='CarePlan#ActivityStatus')

    subactivities = Field(
        'subactivity', 'object',
        binding=SubActivity,
        optional=True,
        multiple=ALL_ITEMS,
        extension='CarePlan#SubActivity')

    prohibited = Field(
        'prohibited', 'boolean',
        optional=True,
        default=False)


@resource_type('CarePlan')
class CarePlan(interfaces.IIdentifiedFHIRResource):

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
        binding=codes.CAREPLAN_STATUS)

    goals = Field(
        'goal', 'object',
        binding=Goal,
        optional=True,
        multiple=ALL_ITEMS)


class ProcessingStatus(zope.interface.Interface):

    status = Field(
        'status', 'code',
        optional=True,
        binding=codes.PROCESSING_STATUS,
        extension='MessageHeader#ProcessingStatusStatus')

    last_changed = Field(
        'statusLastChanged', 'instant',
        extension='MessageHeader#ProcessingStatusStatusLastChanged')

    exception = Field(
        'exception', 'string',
        optional=True,
        extension='MessageHeader#ProcessingStatusException')


class MessageHeaderSource(zope.interface.Interface):

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


class MessageHeaderResponse(zope.interface.Interface):

    identifier = Field(
        'identifier', 'string')

    code = Field(
        'code', 'code',
        binding=codes.MESSAGE_HEADER_RESPONSE_CODE)


@resource_type('MessageHeader')
class MessageHeader(interfaces.IFHIRResource):

    identifier = Field(
        'identifier', 'string')

    timestamp = Field(
        'timestamp', 'instant')

    data = Field(
        'data', 'reference',
        multiple=FIRST_ITEM,
        optional=True)

    patient = Field(
        'patient', 'reference',
        optional=True,
        extension='MessageHeader#Patient')

    event = Field(
        'event', 'coding',
        binding=codes.MESSAGE_HEADER_EVENTS)

    response = Field(
        'response', 'object',
        optional=True,
        binding=MessageHeaderResponse)

    status = Field(
        'processingStatus', 'object',
        optional=True,
        binding=ProcessingStatus,
        extension='MessageHeader#ProcessingStatus')

    source = Field(
        'source', 'object',
        binding=MessageHeaderSource)
