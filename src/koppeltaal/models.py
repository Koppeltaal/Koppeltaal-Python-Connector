import zope.interface
import koppeltaal.definitions
import koppeltaal.interfaces


@zope.interface.implementer(koppeltaal.interfaces.IFHIRResource)
class FHIRResource(object):
    fhir_link = None


@zope.interface.implementer(koppeltaal.definitions.SubActivityDefinition)
class SubActivityDefinition(object):

    def __init__(
            self,
            active=True,
            description=None,
            identifier=None,
            name=None):
        self.active = active
        self.description = description
        self.identifier = identifier
        self.name = name


@zope.interface.implementer(koppeltaal.definitions.ActivityDefinition)
class ActivityDefinition(FHIRResource):

    def __init__(
            self,
            description=None,
            identifier=None,
            is_active=True,
            is_archived=False,
            is_domain_specific=False,
            kind=None,
            launch_type=None,
            name=None,
            performer=None,
            subactivities=None):
        self.description = description
        self.identifier = identifier
        self.is_active = is_active
        self.is_archived = is_archived
        self.is_domain_specific = is_domain_specific
        self.kind = kind
        self.launch_type = launch_type
        self.name = name
        self.performer = performer
        self.subactivities = subactivities


@zope.interface.implementer(koppeltaal.definitions.Name)
class Name(object):

    def __init__(
            self,
            family=None,
            given=None,
            use="official"):
        self.family = family
        self.given = given
        self.use = use


@zope.interface.implementer(koppeltaal.definitions.Contact)
class Contact(object):

    def __init__(
            self,
            system=None,
            value=None,
            use=None):
        self.system = system
        self.value = value
        self.use = use


@zope.interface.implementer(koppeltaal.definitions.Identifier)
class Identifier(object):

    def __init__(
            self,
            system=None,
            value=None,
            use=None):
        self.system = system
        self.value = value
        self.use = use


@zope.interface.implementer(koppeltaal.definitions.Participant)
@zope.interface.implementer(koppeltaal.definitions.ActivityParticipant)
class Participant(object):

    def __init__(
            self,
            member=None,
            role=None):
        self.member = member
        self.role = role


@zope.interface.implementer(koppeltaal.definitions.Patient)
class Patient(FHIRResource):

    def __init__(
            self,
            age=None,
            birth_date=None,
            contact=None,
            identifiers=None,
            name=None):
        self.age = age
        self.birth_date = birth_date
        self.contact = contact
        self.identifiers = identifiers
        self.name = name


@zope.interface.implementer(koppeltaal.definitions.Practitioner)
class Practitioner(FHIRResource):

    def __init__(
            self,
            contact=None,
            identifiers=None,
            name=None):
        self.contact = contact
        self.identifiers = identifiers
        self.name = name


@zope.interface.implementer(koppeltaal.definitions.Goal)
class Goal(object):

    def __init__(
            self,
            description=None,
            notes=None,
            status=None):
        self.description = description
        self.status = status
        self.notes = notes


@zope.interface.implementer(koppeltaal.definitions.SubActivity)
class SubActivity(object):

    def __init__(
            self,
            definition=None,
            status=None):
        self.definition = definition
        self.status = status


@zope.interface.implementer(koppeltaal.definitions.Activity)
class Activity(object):

    def __init__(
            self,
            cancelled=None,
            definition=None,
            description=None,
            finished=None,
            identifier=None,
            kind=None,
            notes=None,
            participants=None,
            planned=None,
            started=None,
            status=None,
            subactivities=None,
            prohibited=False):
        self.cancelled = cancelled
        self.definition = definition
        self.description = description
        self.finished = finished
        self.identifier = identifier
        self.kind = kind
        self.notes = notes
        self.participants = participants
        self.planned = planned
        self.started = started
        self.status = status
        self.subactivities = subactivities
        self.prohibited = prohibited


@zope.interface.implementer(koppeltaal.definitions.CarePlan)
class CarePlan(FHIRResource):

    def __init__(
            self,
            activities=None,
            goals=None,
            participants=None,
            patient=None,
            status=None):
        self.activities = activities
        self.goals = goals
        self.participants = participants
        self.patient = patient
        self.status = status


@zope.interface.implementer(koppeltaal.definitions.ProcessingStatus)
class Status(object):

    def __init__(
            self,
            exception=None,
            last_changed=None,
            status=None):
        self.exception = exception
        self.last_changed = last_changed
        self.status = status


@zope.interface.implementer(koppeltaal.definitions.Source)
class Source(object):

    def __init__(self,
                 endpoint=None,
                 name=None,
                 software=None,
                 version=None):
        self.endpoint = endpoint
        self.name = name
        self.software = software
        self.version = version


@zope.interface.implementer(koppeltaal.definitions.CarePlanSubActivityStatus)
class SubActivityStatus(object):

    def __init__(
            self,
            identifier=None,
            status=None):
        self.identifier = identifier
        self.status = status


@zope.interface.implementer(koppeltaal.definitions.CarePlanActivityStatus)
class ActivityStatus(FHIRResource):

    def __init__(
            self,
            identifier=None,
            status=None,
            subactivities=None):
        self.identifier = identifier
        self.status = status
        self.subactivities = subactivities


@zope.interface.implementer(koppeltaal.definitions.MessageHeader)
class MessageHeader(FHIRResource):

    def __init__(
            self,
            data=None,
            event=None,
            identifier=None,
            patient=None,
            source=None,
            status=None,
            timestamp=None):
        self.data = data
        self.event = event
        self.identifier = identifier
        self.patient = patient
        self.source = source
        self.status = status
        self.timestamp = timestamp
