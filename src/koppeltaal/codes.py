# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import koppeltaal.interfaces

NULL_SYSTEM = 'http://hl7.org/fhir/v3/NullFlavor'
NULL_VALUE = 'UNK'


class Code(dict):

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
                "display": self[value],
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
    {'Game': 'Game',
     'ELearning': 'ELearning',
     'Questionnaire': 'Questionnaire',
     'Meeting': 'Meeting',
     'MultipleActivityTemplate': 'MultipleActivityTemplate'})

ACTIVITY_PERFORMER = Code(
    'ActivityPerformer',
    {'Patient': 'Patient',
     'Practitioner': 'Practitioner',
     'RelatedPerson': 'RelatedPerson'})

ACTIVITY_LAUNCH_TYPE = Code(
    'ActivityDefinitionLaunchType',
    {'Web': 'Web',
     'Mobile': 'Mobile',
     'Node': 'Node'})


CAREPLAN_ACTIVITY_CATEGORY = Code(
    'http://hl7.org/fhir/care-plan-activity-category',
    {'diet': 'diet',
     'drug': 'drug',
     'encounter': 'encounter',
     'observation': 'observation',
     'procedure': 'procedure',
     'supply': 'supply',
     'other': 'other'})


CAREPLAN_ACTIVITY_STATUS = Code(
    'CarePlanActivityStatus',
    {'Waiting': 'Waiting',
     'Available': 'Available',
     'InProgress': 'InProgress',
     'Completed': 'Completed',
     'Cancelled': 'Cancelled',
     'Expired': 'Expired',
     'SkippedByUser': 'SkippedByUser'})

CAREPLAN_PARTICIPANT_ROLE = Code(
    'CarePlanParticipantRole',
    {'Requester': 'Requester',
     'Supervisor': 'Supervisor',
     'Thirdparty': 'Thirdparty',
     'Caregiver': 'Caregiver',
     'Secretary': 'Secretary',
     'Analyst': 'Analyst'})

CAREPLAN_STATUS = Code(
    'http://hl7.org/fhir/care-plan-status',
    {'planned': 'planned',
     'active': 'active',
     'completed': 'completed'})

CAREPLAN_GOAL_STATUS = Code(
    'http://hl7.org/fhir/care-plan-goal-status',
    {'in progress': 'in progress',
     'achieved': 'achieved',
     'sustaining': 'sustaining',
     'cancelled': 'cancelled'})

CONTACT_SYSTEM = Code(
    'http://hl7.org/fhir/contact-system',
    {'phone': 'phone',
     'fax': 'fax',
     'url': 'url',
     'email': 'email'})

CONTACT_USE = Code(
    'http://hl7.org/fhir/contact-use',
    {'home': 'home',
     'work': 'work',
     'temp': 'temp',
     'old': 'old',
     'mobile': 'mobile'})

CONTACT_ENTITY_TYPE = Code(
    'http://hl7.org/fhir/contactentity-type',
    {'BILL': 'BILL',
     'ADMIN': 'ADMIN',
     'HR': 'HR',
     'PAYOR': 'PAYOR',
     'PATINF': 'PATINF',
     'PRESS': 'PRESS'})

DEVICE_KIND = Code(
    'DeviceKind',
    {'Application': 'Application'})

GENDER = Code(
    'http://hl7.org/fhir/v3/AdministrativeGender',
    {'F': 'Female', 'M': 'Male', 'UN': 'Undifferentiated'})

IDENTIFIER_USE = Code(
    'http://hl7.org/fhir/identifier-use',
    {'usual': 'usual',
     'official': 'official',
     'temp': 'temp',
     'secondary': 'secondary'})


MESSAGE_HEADER_RESPONSE_CODE = Code(
    'http://hl7.org/fhir/response-code',
    {'fatal-error': 'fatal-error',
     'ok': 'ok',
     'transient-error': 'transient-error'})

MESSAGE_HEADER_EVENTS = Code(
    'MessageEvents',
    {'CreateOrUpdateActivityDefinition': 'CreateOrUpdateActivityDefinition',
     'CreateOrUpdateCarePlan': 'CreateOrUpdateCarePlan',
     'CreateOrUpdateCarePlanActivityResult':
        'CreateOrUpdateCarePlanActivityResult',
     'CreateOrUpdatePatient': 'CreateOrUpdatePatient',
     'CreateOrUpdatePractitioner': 'CreateOrUpdatePractitioner',
     'CreateOrUpdateRelatedPerson': 'CreateOrUpdateRelatedPerson',
     'CreateOrUpdateUserMessage': 'CreateOrUpdateUserMessage',
     'UpdateCarePlanActivityStatus': 'UpdateCarePlanActivityStatus',
     })

MESSAGE_KIND = Code(
    'UserMessageKind',
    {'Alert': 'Alert',
     'Advice': 'Advice',
     'Question': 'Question',
     'Answer': 'Answer',
     'Notification': 'Notification',
     'Message': 'Message',
     'Request': 'Request'})

NAME_USE = Code(
    'http://hl7.org/fhir/name-use',
    {'usual': 'usual',
     'official': 'official',
     'temp': 'temp',
     'nickname': 'nickname',
     'anonymous': 'anonymous',
     'old': 'old',
     'maiden': 'maiden'})

ORGANIZATION_TYPE = Code(
    'http://hl7.org/fhir/organization-type',
    {'dept': 'dept',
     'icu': 'icu',
     'team': 'team',
     'fed': 'fed',
     'ins': 'ins',
     'edu': 'edu',
     'reli': 'reli',
     'pharm': 'pharm'})

PROCESSING_STATUS = Code(
    'ProcessingStatus',
    {'Claimed': 'Claimed',
     'Failed': 'Failed',
     'MaximumRetriesExceeded': 'MaximumRetriesExceeded',
     'New': 'New',
     'ReplacedByNewVersion': 'ReplacedByNewVersion',
     'Success': 'Success'})

# BlackBoxState is not valid, but the javascript connector generate
# some of those.
OTHER_RESOURCE_USAGE = Code(
    'OtherResourceUsage',
    {'ActivityDefinition': 'ActivityDefinition',
     'BlackBoxState': 'BlackBoxState',
     'CarePlanActivityStatus': 'CarePlanActivityStatus',
     'CareTeam': 'CareTeam',
     'StorageItem': 'StorageItem',
     'UserMessage': 'UserMessage'})

