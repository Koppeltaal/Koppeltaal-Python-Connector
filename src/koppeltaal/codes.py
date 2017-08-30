# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import koppeltaal.interfaces

NULL_SYSTEM = 'http://hl7.org/fhir/v3/NullFlavor'
NULL_VALUE = 'UNK'


class Code(list):

    def __init__(self, system, items):
        super(Code, self).__init__(items)
        if not system.startswith('http:'):
            system = koppeltaal.interfaces.NAMESPACE + system
        self.system = system

    def pack_code(self, value):
        if value not in self:
            raise koppeltaal.interfaces.InvalidCode(self, value)
        return value

    def pack_coding(self, value):
        if value not in self:
            raise koppeltaal.interfaces.InvalidCode(self, value)
        return {"code": value,
                "display": value,
                "system": self.system}

    def unpack_code(self, code):
        if code not in self:
            raise koppeltaal.interfaces.InvalidCode(self, code)
        return code

    def unpack_coding(self, coding):
        value = coding.get("code")
        system = coding.get("system")
        if system == NULL_SYSTEM and value == NULL_VALUE:
            return None
        if system != self.system:
            raise koppeltaal.interfaces.InvalidSystem(self, system)
        if value not in self:
            raise koppeltaal.interfaces.InvalidCode(self, value)
        return value


ACTIVITY_KIND = Code(
    'ActivityKind',
    ['Game',
     'ELearning',
     'Questionnaire',
     'Meeting',
     'MultipleActivityTemplate'])

ACTIVITY_PERFORMER = Code(
    'ActivityPerformer',
    ['Patient',
     'Practitioner',
     'RelatedPerson'])

ACTIVITY_LAUNCH_TYPE = Code(
    'ActivityDefinitionLaunchType',
    ['Web',
     'Mobile',
     'Node'])

CAREPLAN_ACTIVITY_STATUS = Code(
    'CarePlanActivityStatus',
    ['Waiting',
     'Available',
     'InProgress',
     'Completed',
     'Cancelled',
     'Expired',
     'SkippedByUser'])

CAREPLAN_PARTICIPANT_ROLE = Code(
    'CarePlanParticipantRole',
    ['Requester',
     'Supervisor',
     'Thirdparty',
     'Caregiver',
     'Secretary',
     'Analyst'])

CAREPLAN_STATUS = Code(
    'http://hl7.org/fhir/care-plan-status',
    ['planned',
     'active',
     'completed'])

CAREPLAN_GOAL_STATUS = Code(
    'http://hl7.org/fhir/care-plan-goal-status',
    ['in progress',
     'achieved',
     'sustaining',
     'cancelled'])

CONTACT_SYSTEM = Code(
    'http://hl7.org/fhir/contact-system',
    ['phone',
     'fax',
     'url',
     'email'])

CONTACT_USE = Code(
    'http://hl7.org/fhir/contact-use',
    ['home',
     'work',
     'temp',
     'old',
     'mobile'])

CONTACT_ENTITY_TYPE = Code(
    'http://hl7.org/fhir/contactentity-type',
    ['BILL',
     'ADMIN',
     'HR',
     'PAYOR',
     'PATINF',
     'PRESS'])

DEVICE_KIND = Code(
    'DeviceKind',
    ['Application'])

GENDER = Code(
    'http://hl7.org/fhir/v3/AdministrativeGender',
    ['F', 'M', 'UN'])

IDENTIFIER_USE = Code(
    'http://hl7.org/fhir/identifier-use',
    ['usual',
     'official',
     'temp',
     'secondary'])


MESSAGE_HEADER_RESPONSE_CODE = Code(
    'http://hl7.org/fhir/response-code',
    ['fatal-error',
     'ok',
     'transient-error'])

MESSAGE_HEADER_EVENTS = Code(
    'MessageEvents',
    ['CreateOrUpdateActivityDefinition',
     'CreateOrUpdateCarePlan',
     'CreateOrUpdateCarePlanActivityResult',
     'CreateOrUpdatePatient',
     'CreateOrUpdatePractitioner',
     'CreateOrUpdateRelatedPerson',
     'CreateOrUpdateUserMessage',
     'UpdateCarePlanActivityStatus',
     ])

MESSAGE_KIND = Code(
    'UserMessageKind',
    ['Alert',
     'Advice',
     'Question',
     'Answer',
     'Notification',
     'Message',
     'Request'])

NAME_USE = Code(
    'http://hl7.org/fhir/name-use',
    ['usual',
     'official',
     'temp',
     'nickname',
     'anonymous',
     'old',
     'maiden'])

ORGANIZATION_TYPE = Code(
    'http://hl7.org/fhir/organization-type',
    ['dept',
     'icu',
     'team',
     'fed',
     'ins',
     'edu',
     'reli',
     'pharm'])

PROCESSING_STATUS = Code(
    'ProcessingStatus',
    ['Claimed',
     'Failed',
     'MaximumRetriesExceeded',
     'New',
     'ReplacedByNewVersion',
     'Success'])

# BlackBoxState is not valid, but the javascript connector generate
# some of those.
OTHER_RESOURCE_USAGE = Code(
    'OtherResourceUsage',
    ['ActivityDefinition',
     'BlackBoxState',
     'CarePlanActivityStatus',
     'StorageItem',
     'UserMessage'])
