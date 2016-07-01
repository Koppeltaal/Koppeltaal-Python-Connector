import koppeltaal.interfaces


class Code(list):

    def __init__(self, name, items):
        super(Code, self).__init__(items)
        self.name = name

    @property
    def fdqn(self):
        return koppeltaal.interfaces.NAMESPACE + self.name

    def pack(self, value):
        if value not in self:
            raise ValueError(value)
        return {"code": value,
                "display": value,
                "system": self.fqdn}

    def unpack(self, package):
        value = package["code"]
        if value not in self:
            raise ValueError(value)
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

PROCESSING_STATUS = Code(
    'ProcessingStatus',
    ['New',
     'Claimed',
     'Success',
     'Failed',
     'ReplacedByNewVersion'])
