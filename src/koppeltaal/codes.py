import koppeltaal.interfaces


class Code(list):

    def __init__(self, name, items, system=None):
        super(Code, self).__init__(items)
        self.name = name
        if system is None:
            system = koppeltaal.interfaces.NAMESPACE + self.name
        self.system = system

    def pack(self, value):
        if value not in self:
            raise ValueError(value)
        return {"code": value,
                "display": value,
                "system": self.system}

    def unpack(self, package):
        value = package["code"]
        if value not in self:
            raise koppeltaal.interfaces.InvalidValue(value, self)
        return value


ACTIVITY_KIND = Code(
    'ActivityKind',
    ['Game',
     'ELearning',
     'Questionnaire',
     'Meeting'])

ACTIVITY_PERFORMER = Code(
    'ActivityPerformer',
    ['Patient',
     'Practitioner',
     'RelatedPerson'])

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
    ['Requester'
     'Supervisor'
     'Thirdparty'
     'Caregiver'
     'Secretary'
     'Analyst'])

CAREPLAN_STATUS = Code(
    'CarePlanStatus',
    ['planned',
     'active',
     'completed'],
    'http://hl7.org/fhir/care-plan-status')

CAREPLAN_GOAL_STATUS = Code(
    'CarePlanGoalStatus',
    ['in progress',
     'achieved',
     'sustaining',
     'cancelled'],
    'http://hl7.org/fhir/care-plan-goal-status')

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
    'NameUse',
    ['usual',
     'official'
     'temp',
     'nickname',
     'anonymous',
     'old',
     'maiden'],
    'http://hl7.org/fhir/name-use')

PROCESSING_STATUS = Code(
    'ProcessingStatus',
    ['New',
     'Claimed',
     'Success',
     'Failed',
     'ReplacedByNewVersion'])

GENDER = Code(
    'AdministrativeGender',
    ['F', 'M', 'UN'],
    'http://hl7.org/fhir/v3/AdministrativeGender')
