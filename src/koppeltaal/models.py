import zope.interface
import koppeltaal.definitions


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
class ActivityDefinition(object):
    fhir_link = None

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

    def __format__(self, _):
        return (
            '<ActivityDefinition '
            'identifier="{}" name="{}" kind="{}"/>').format(
                self.identifier, self.name, self.kind)


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

    def __format__(self, _):
        return '{}, {} ({})'.format(self.family, self.given, self.use)


@zope.interface.implementer(koppeltaal.definitions.Participant)
class Participant(object):

    def __init__(
            self,
            member=None,
            role=None):
        self.member = member
        self.role = role

    def __format__(self, _):
        return '<Participant>{}</Participant>'.format(self.member)


@zope.interface.implementer(koppeltaal.definitions.Patient)
class Patient(object):
    fhir_link = None

    def __init__(
            self,
            age=None,
            birth_date=None,
            name=None):
        self.name = name
        self.age = age
        self.birth_date = birth_date

    def __format__(self, _):
        return '<Patient name="{}"/>'.format(self.name)


@zope.interface.implementer(koppeltaal.definitions.Practitioner)
class Practitioner(object):
    fhir_link = None

    def __init__(
            self,
            name=None):
        self.name = name

    def __format__(self, _):
        return '<Practitioner name="{}"/>'.format(self.name)


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

    def __format__(self, _):
        return '<Goal status="{}">{} {}</Goal>'.format(
            self.status, self.description, self.notes)


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
            subactivities=None):
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


@zope.interface.implementer(koppeltaal.definitions.CarePlan)
class CarePlan(object):
    fhir_link = None

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

    def __format__(self, _):
        return '<CarePlan status="{}">{} {} {}</CarePlan>'.format(
            self.status,
            self.patient or "<Patient/>",
            ', '.join('{}'.format(p) for p in self.participants),
            ', '.join('{}'.format(g) for g in self.goals))


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


@zope.interface.implementer(koppeltaal.definitions.MessageHeader)
class MessageHeader(object):
    fhir_link = None

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

    def __format__(self, _):
        return ('<Message event="{}" status="{}" last_changed"{}">'
                '{}{}</Message>').format(
                    self.event,
                    self.status.status,
                    self.status.last_changed,
                    self.patient or "<Patient/>",
                    self.data or "<Data/>")
