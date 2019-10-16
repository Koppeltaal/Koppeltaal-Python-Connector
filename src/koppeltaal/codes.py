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
        display = self[value]
        coding = {"code": value, "system": self.system}
        if display is not None:
            coding["display"] = display
        return coding

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
    {'ELearning': 'E-Learning',
     'Game': 'Game',
     'Meeting': 'Meeting',
     'MultipleActivityTemplate': 'Multiple activity template',
     'Questionnaire': 'Questionnaire',
     })

ACTIVITY_LAUNCH_TYPE = Code(
    'ActivityDefinitionLaunchType',
    {'Mobile': 'Mobile',
     'None': 'None',
     'Web': 'Web',
     })

ACTIVITY_PERFORMER = Code(
    'ActivityPerformer',
    {'Practitioner': 'Practitioner',
     'RelatedPerson': 'RelatedPerson',
     'Patient': 'Patient',
     })

ADDRESS_USE = Code(
    'http://hl7.org/fhir/address-use',
    {'home': 'home',
     'old': 'old',
     'temp': 'temp',
     'work': 'work',
     })

CAREPLAN_ACTIVITY_CATEGORY = Code(
    'http://hl7.org/fhir/care-plan-activity-category',
    {'diet': 'diet',
     'drug': 'drug',
     'encounter': 'encounter',
     'observation': 'observation',
     'other': 'other',
     'procedure': 'procedure',
     'supply': 'supply',
     })

CAREPLAN_PARTICIPANT_ROLE = Code(
    'CarePlanParticipantRole',
    {'Analyst': 'Analyst',
     'Caregiver': 'Caregiver',
     'Secretary': 'Secretary',
     'Supervisor': 'Supervisor',
     'Thirdparty': 'Thirdparty',
     'Requester': 'Requester',
     })

CAREPLAN_ACTIVITY_STATUS = Code(
    'CarePlanActivityStatus',
    {'Available': 'Available',
     'Cancelled': 'Cancelled',
     'Completed': 'Completed',
     'Expired': 'Expired',
     'InProgress': 'InProgress',
     'SkippedByUser': 'SkippedByUser',
     'Waiting': 'Waiting',
     })

CAREPLAN_GOAL_STATUS = Code(
    'http://hl7.org/fhir/care-plan-goal-status',
    {'achieved': 'achieved',
     'cancelled': 'cancelled',
     'in progress': 'in progress',
     'sustaining': 'sustaining',
     })

CAREPLAN_STATUS = Code(
    'http://hl7.org/fhir/care-plan-status',
    {'active': 'active',
     'completed': 'completed',
     'planned': 'planned',
     })

CONTACT_SYSTEM = Code(
    'http://hl7.org/fhir/contact-system',
    {'email': 'email',
     'fax': 'fax',
     'phone': 'phone',
     'url': 'url',
     })

CARE_TEAM_STATUS = Code(
    'CareTeamStatus',
    {'active': 'Active',
     'entered-in-error': 'Entered in error',
     'inactive': 'Inactive',
     'proposed': 'Proposed',
     'suspended': 'Suspended',
     })

CONTACT_ENTITY_TYPE = Code(
    'http://hl7.org/fhir/contactentity-type',
    {'ADMIN': 'ADMIN',
     'BILL': 'BILL',
     'HR': 'HR',
     'PATINF': 'PATINF',
     'PAYOR': 'PAYOR',
     'PRESS': 'PRESS',
     })

CONTACT_USE = Code(
    'http://hl7.org/fhir/contact-use',
    {'home': 'home',
     'mobile': 'mobile',
     'old': 'old',
     'temp': 'temp',
     'work': 'work',
     })

DEVICE_KIND = Code(
    'DeviceKind',
    {'Application': 'Application'})

GENDER = Code(
    'http://hl7.org/fhir/v3/AdministrativeGender',
    {'F': 'Female',
     'M': 'Male',
     'UN': 'Undifferentiated',
     })

IDENTIFIER_USE = Code(
    'http://hl7.org/fhir/identifier-use',
    {'official': 'official',
     'secondary': 'secondary',
     'temp': 'temp',
     'usual': 'usual',
     })

MESSAGE_HEADER_RESPONSE_CODE = Code(
    'http://hl7.org/fhir/response-code',
    {'fatal-error': 'fatal-error',
     'ok': 'ok',
     'transient-error': 'transient-error',
     })

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
    {'Advice': 'Advice',
     'Alert': 'Alert',
     'Answer': 'Answer',
     'Message': 'Message',
     'Notification': 'Notification',
     'Question': 'Question',
     'Request': 'Request',
     })

NAME_USE = Code(
    'http://hl7.org/fhir/name-use',
    {'anonymous': 'anonymous',
     'maiden': 'maiden',
     'nickname': 'nickname',
     'official': 'official',
     'old': 'old',
     'temp': 'temp',
     'usual': 'usual',
     })

ORGANIZATION_TYPE = Code(
    'http://hl7.org/fhir/organization-type',
    {'dept': 'dept',
     'edu': 'edu',
     'fed': 'fed',
     'icu': 'icu',
     'ins': 'ins',
     'pharm': 'pharm',
     'reli': 'reli',
     'team': 'team',
     })

# BlackBoxState is not valid, but the javascript connector generate
# some of those.
OTHER_RESOURCE_USAGE = Code(
    'OtherResourceUsage',
    {'ActivityDefinition': 'ActivityDefinition',
     'BlackBoxState': 'BlackBoxState',
     'CarePlanActivityStatus': 'CarePlanActivityStatus',
     'CareTeam': 'CareTeam',
     'StorageItem': 'StorageItem',
     'UserMessage': 'UserMessage',
     })


PROCESSING_STATUS = Code(
    'ProcessingStatus',
    {'Claimed': 'Claimed',
     'Failed': 'Failed',
     'MaximumRetriesExceeded': 'MaximumRetriesExceeded',
     'New': 'New',
     'ReplacedByNewVersion': 'ReplacedByNewVersion',
     'Success': 'Success',
     })


ISSUE_TYPE = Code(
    'http://hl7.org/fhir/issue-type',
    {'invalid': None,
     'structure': None,
     'required': None,
     'value': None,
     'invariant': None,
     'security': None,
     'login': None,
     'unknown': None,
     'expired': None,
     'forbidden': None,
     'processing': None,
     'not-supported': None,
     'duplicate': None,
     'not-found': None,
     'too-long': None,
     'code-unknown': None,
     'extension': None,
     'too-costly': None,
     'business-rule': None,
     'conflict': None,
     'transient': None,
     'lock-error': None,
     'no-store': None,
     'exception': None,
     'timeout': None,
     'throttled': None,
     })


ISSUE_SEVERITY = Code(
    'http://hl7.org/fhir/issue-severity',
    {'fatal': None,
     'error': None,
     'warning': None,
     'information': None,
     })
