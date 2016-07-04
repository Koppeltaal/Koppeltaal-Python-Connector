
class SubActivityDefinition(object):
    name = None
    identifier = None
    description = None
    active = True


class ActivityDefinition(object):
    uid = None

    identifier = None
    kind = None
    name = None
    subactivities = None
    description = None
    is_active = True
    is_domain_specific = False
    is_archived = False

    def __format__(self, _):
        return (
            '<ActivityDefinition '
            'identifier="{}" name="{}" kind="{}"/>').format(
                self.identifier, self.name, self.kind)


class Name(object):
    family = None
    given = None
    use = None

    def __format__(self, _):
        return '{}, {} ({})'.format(self.family, self.given, self.use)


class Participant(object):
    member = None
    role = None  # XXX

    def __format__(self, _):
        return '<Participant>{}</Participant>'.format(self.member)


class Patient(object):
    uid = None
    name = None

    def __format__(self, _):
        return '<Patient name="{}"/>'.format(self.name)


class Practitioner(object):
    uid = None
    name = None

    def __format__(self, _):
        return '<Practitioner name="{}"/>'.format(self.name)


class Goal(object):
    description = None
    status = None
    notes = None

    def __format__(self, _):
        return '<Goal status="{}">{} {}</Goal>'.format(
            self.status, self.description, self.notes)


class Activity(object):
    cancelled = None
    definition = None
    description = None
    finished = None
    kind = None
    notes = None
    participants = None
    planned = None
    started = None
    status = None
    subactivities = None


class CarePlan(object):
    uid = None

    status = None
    patient = None
    participants = None
    goals = None

    def __format__(self, _):
        return '<CarePlan status="{}">{} {} {}</CarePlan>'.format(
            self.status,
            self.patient or "<Patient/>",
            ', '.join('{}'.format(p) for p in self.participants),
            ', '.join('{}'.format(g) for g in self.goals))


class Status(object):
    status = None
    last_changed = None
    exception = None


class Source(object):
    name = None
    software = None
    version = None
    endpoint = None


class Message(object):
    uid = None

    timestamp = None
    data = None
    patient = None
    event = None
    status = None

    def __format__(self, _):
        return ('<Message event="{}" status="{}" last_changed"{}">'
                '{}{}</Message>').format(
                    self.event,
                    self.status.status,
                    self.status.last_changed,
                    self.patient or "<Patient/>",
                    self.data or "<Data/>")
