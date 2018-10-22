# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

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
            binding=None,
            default=None,
            extension=None,
            multiple=False,
            optional=False,
            reserved_allowed=False):
        super(Field, self).__init__(__name__='')
        assert reserved_allowed or name not in RESERVED_NAMES, \
            '{} is a reserved name.'
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
        'description', 'string',
        optional=True,
        extension='ActivityDefinition#SubActivityDescription')

    active = Field(
        'isActive', 'boolean',
        default=True,
        extension='ActivityDefinition#SubActivityIsActive',
        optional=True)


@resource_type('ActivityDefinition', False)
class ActivityDefinition(interfaces.IIdentifiedFHIRResource):

    application = Field(
        'application', 'reference',
        extension='ActivityDefinition#Application')

    # Note that this is not required in the specification but his in
    # practice so that other messages can refer to it.
    identifier = Field(
        'activityDefinitionIdentifier', 'string',
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
        extension='ActivityDefinition#ActivityDescription',
        optional=True)

    subactivities = Field(
        'subActivity', 'object',
        binding=SubActivityDefinition,
        extension='ActivityDefinition#SubActivity',
        multiple=ALL_ITEMS,
        optional=True)

    performer = Field(
        'defaultPerformer', 'coding',
        binding=codes.ACTIVITY_PERFORMER,
        extension='ActivityDefinition#DefaultPerformer',
        optional=True)

    launch_type = Field(
        'launchType', 'code',
        binding=codes.ACTIVITY_LAUNCH_TYPE,
        default='Web',
        extension='ActivityDefinition#LaunchType',
        optional=True)

    is_active = Field(
        'isActive', 'boolean',
        default=True,
        extension='ActivityDefinition#IsActive',
        optional=True)

    is_domain_specific = Field(
        'isDomainSpecific', 'boolean',
        extension='ActivityDefinition#IsDomainSpecific',
        optional=True)

    is_archived = Field(
        'isArchived', 'boolean',
        default=False,
        extension='ActivityDefinition#IsArchived',
        optional=True)


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
        extension='CarePlanActivityStatus#PercentageCompleted')


class Name(zope.interface.Interface):

    # http://hl7.org/fhir/DSTU1/datatypes.html#HumanName

    given = Field(
        'given', 'string',
        multiple=ALL_ITEMS,
        optional=True)

    family = Field(
        'family', 'string',
        multiple=ALL_ITEMS,
        optional=True)

    prefix = Field(
        'prefix', 'string',
        multiple=ALL_ITEMS,
        optional=True)

    suffix = Field(
        'suffix', 'string',
        multiple=ALL_ITEMS,
        optional=True)

    use = Field(
        'use', 'code',
        binding=codes.NAME_USE,
        optional=True)


class Contact(zope.interface.Interface):

    system = Field(
        'system', 'code',
        binding=codes.CONTACT_SYSTEM,
        optional=True)

    value = Field(
        'value', 'string',
        optional=True)

    use = Field(
        'use', 'code',
        binding=codes.CONTACT_USE,
        optional=True)


class Identifier(zope.interface.Interface):

    system = Field(
        'system', 'string',
        optional=True)

    value = Field(
        'value', 'string',
        optional=True)

    use = Field(
        'use', 'code',
        binding=codes.IDENTIFIER_USE,
        optional=True)


class OrganizationContactPerson(zope.interface.Interface):

    contacts = Field(
        'telecom', 'object',
        binding=Contact,
        multiple=ALL_ITEMS,
        optional=True)

    gender = Field(
        'gender', 'codeable',
        binding=codes.GENDER,
        optional=True)

    name = Field(
        'name', 'object',
        binding=Name,
        optional=True)

    purpose = Field(
        'purpose', 'code',
        binding=codes.CONTACT_ENTITY_TYPE,
        optional=True)


@resource_type('Organization')
class Organization(interfaces.IIdentifiedFHIRResource):

    active = Field(
        'active', 'boolean',
        optional=True)

    category = Field(
        'type', 'code',
        binding=codes.ORGANIZATION_TYPE,
        optional=True)

    contacts = Field(
        'telecom', 'object',
        binding=Contact,
        multiple=ALL_ITEMS,
        optional=True)

    contact_persons = Field(
        'contact', 'object',
        binding=OrganizationContactPerson,
        multiple=ALL_ITEMS,
        optional=True)

    identifiers = Field(
        'identifier', 'object',
        binding=Identifier,
        multiple=ALL_ITEMS,
        optional=True)

    name = Field(
        'name', 'string',
        optional=True)

    part_of = Field(
        'partOf', 'reference',
        optional=True)


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

    care_providers = Field(
        'careProvider', 'reference',
        multiple=ALL_ITEMS,
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
        multiple=ALL_ITEMS)

    managing_organization = Field(
        'managingOrganization', 'reference',
        optional=True)


@resource_type('Practitioner')
class Practitioner(interfaces.IIdentifiedFHIRResource):

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

    name = Field(
        'name', 'object',
        binding=Name,
        optional=True)

    gender = Field(
        'gender', 'codeable',
        binding=codes.GENDER,
        optional=True)

    organization = Field(
        'organization', 'reference',
        optional=True)


class Participant(zope.interface.Interface):

    member = Field(
        'member', 'reference')

    role = Field(
        'role', 'codeable',
        binding=codes.CAREPLAN_PARTICIPANT_ROLE,
        optional=True)

    careteam = Field(
        'careteam', 'reference',
        extension='CarePlan#ParticipantCareTeam',
        multiple=ALL_ITEMS,
        optional=True)


class Goal(zope.interface.Interface):

    description = Field(
        'description', 'string')

    status = Field(
        'status', 'code',
        binding=codes.CAREPLAN_GOAL_STATUS,
        optional=True)

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
        'status', 'coding',
        binding=codes.CAREPLAN_ACTIVITY_STATUS,
        extension='CarePlan#SubActivityStatus',
        optional=True)


class ActivityParticipant(zope.interface.Interface):

    member = Field(
        'member', 'reference',
        extension='CarePlan#ParticipantMember')

    role = Field(
        'role', 'codeable',
        binding=codes.CAREPLAN_PARTICIPANT_ROLE,
        extension='CarePlan#ParticipantRole',
        optional=True)

    careteam = Field(
        'careteam', 'reference',
        extension='CarePlan#ParticipantCareTeam',
        multiple=ALL_ITEMS,
        optional=True)


class ActivityDetails(zope.interface.Interface):

    category = Field(
        'category', 'code',
        binding=codes.CAREPLAN_ACTIVITY_CATEGORY)

    performers = Field(
        'performer', 'reference',
        multiple=ALL_ITEMS,
        optional=True)


class Activity(zope.interface.Interface):

    # This is optional in the specification but cannot be in practice,
    # or other messages won't be able to refer to it.
    identifier = Field(
        'identifier', 'string',
        extension='CarePlan#ActivityIdentifier')

    cancelled = Field(
        'cancelled', 'instant',
        extension='CarePlan#Cancelled',
        optional=True)

    # Note how this definition "points" to the `identifier` one of the
    # `ActivityDefinition`.
    definition = Field(
        'definition', 'string',
        extension='CarePlan#ActivityDefinition',
        optional=True)

    description = Field(
        'description', 'string',
        extension='CarePlan#ActivityDescription',
        optional=True)

    ends = Field(
        'endDate', 'datetime',
        extension='CarePlan#EndDate',
        optional=True)

    finished = Field(
        'finished', 'instant',
        extension='CarePlan#Finished',
        optional=True)

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
        extension='CarePlan#Participant',
        multiple=ALL_ITEMS,
        optional=True)

    planned = Field(
        'startDate', 'datetime',
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
        extension='CarePlan#SubActivity',
        multiple=ALL_ITEMS,
        optional=True)

    details = Field(
        'simple', 'object',
        binding=ActivityDetails,
        optional=True)

    prohibited = Field(
        'prohibited', 'boolean',
        default=False,
        optional=True)


@resource_type('CarePlan')
class CarePlan(interfaces.IIdentifiedFHIRResource):

    activities = Field(
        'activity', 'object',
        binding=Activity,
        multiple=ALL_ITEMS,
        optional=True)

    goals = Field(
        'goal', 'object',
        binding=Goal,
        multiple=ALL_ITEMS,
        optional=True)

    participants = Field(
        'participant', 'object',
        binding=Participant,
        multiple=ALL_ITEMS,
        optional=True)

    patient = Field(
        'patient', 'reference',
        optional=True)

    status = Field(
        'status', 'code',
        binding=codes.CAREPLAN_STATUS)


class ProcessingStatus(zope.interface.Interface):

    status = Field(
        'status', 'code',
        binding=codes.PROCESSING_STATUS,
        extension='MessageHeader#ProcessingStatusStatus',
        optional=True)

    last_changed = Field(
        'statusLastChanged', 'instant',
        extension='MessageHeader#ProcessingStatusStatusLastChanged')

    exception = Field(
        'exception', 'string',
        extension='MessageHeader#ProcessingStatusException',
        optional=True)


class MessageHeaderSource(zope.interface.Interface):

    name = Field(
        'name', 'string',
        optional=True)

    software = Field('software', 'string')

    version = Field(
        'version', 'string',
        optional=True)

    endpoint = Field('endpoint', 'string')


class MessageHeaderResponse(zope.interface.Interface):

    identifier = Field('identifier', 'string')

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
        extension='MessageHeader#Patient',
        optional=True)

    event = Field(
        'event', 'coding',
        binding=codes.MESSAGE_HEADER_EVENTS)

    response = Field(
        'response', 'object',
        binding=MessageHeaderResponse,
        optional=True)

    status = Field(
        'processingStatus', 'object',
        binding=ProcessingStatus,
        extension='MessageHeader#ProcessingStatus',
        optional=True)

    source = Field(
        'source', 'object',
        binding=MessageHeaderSource,
        optional=True)


class Period(zope.interface.Interface):

    start = Field(
        'start', 'datetime',
        optional=True)

    end = Field(
        'end', 'datetime',
        optional=True)


@resource_type('CareTeam')
class CareTeam(interfaces.IIdentifiedFHIRResource):

    identifier = Field(
        'careTeamIdentifier', 'object',
        binding=Identifier,
        extension='CareTeam#CareTeamIdentifier',
        multiple=ALL_ITEMS,
        optional=True)

    status = Field(
        'status', 'coding',
        binding=codes.CARE_TEAM_STATUS,
        extension='CareTeam#Status',
        optional=True)

    name = Field(
        'name', 'string',
        extension='CareTeam#Name',
        optional=True)

    subject = Field(
        'subject', 'reference',
        extension='CareTeam#Subject',
        optional=True)

    period = Field(
        'period', 'object',
        binding=Period,
        extension='CareTeam#Period',
        optional=True)

    managing_organization = Field(
        'managingOrganization', 'reference',
        extension='CareTeam#ManagingOrganization',
        multiple=ALL_ITEMS,
        optional=True)


# class Address(zope.interface.Interface):
#
#     use
#     text
#     line
#     city
#     state
#     zip
#     country
#     period
