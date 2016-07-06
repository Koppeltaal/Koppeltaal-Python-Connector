import koppeltaal.interfaces


class Code(list):

    def __init__(self, system, items):
        super(Code, self).__init__(items)
        if not system.startswith('http:'):
            system = koppeltaal.interfaces.NAMESPACE + system
        self.system = system

    def pack_code(self, value):
        if value not in self:
            raise koppeltaal.interfaces.InvalidValue(self, value)
        return value

    def pack_coding(self, value):
        if value not in self:
            raise koppeltaal.interfaces.InvalidValue(self, value)
        return {"code": value,
                "display": value,
                "system": self.system}

    def unpack_code(self, code):
        if code not in self:
            raise koppeltaal.interfaces.InvalidValue(self, code)
        return code

    def unpack_coding(self, coding):
        value = coding["code"]
        if coding.get('system') != self.system:
            raise koppeltaal.interfaces.InvalidValue(self, value)
        if value not in self:
            raise koppeltaal.interfaces.InvalidValue(self, value)
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

DEVICE_KIND = Code(
    'DeviceKind',
    ['Application'])

MESSAGE_EVENTS = Code(
    'MessageEvents',
    ['CreateOrUpdatePatient',
     'CreateOrUpdatePractitioner',
     'CreateOrUpdateRelatedPerson',
     'CreateOrUpdateCarePlan',
     'UpdateCarePlanActivityStatus',
     'CreateOrUpdateCarePlanActivityResult',
     'CreateOrUpdateUserMessage',
     'CreateOrUpdateUserActivityDefinition'])

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

PROCESSING_STATUS = Code(
    'ProcessingStatus',
    ['New',
     'Claimed',
     'Success',
     'Failed',
     'ReplacedByNewVersion'])

GENDER = Code(
    'http://hl7.org/fhir/v3/AdministrativeGender',
    ['F', 'M', 'UN'])

OTHER_RESOURCE_USAGE = Code(
    'OtherResourceUsage',
    ['ActivityDefinition',
     'UserMessage',
     'CarePlanActivityStatus',
     'StorageItem'])
