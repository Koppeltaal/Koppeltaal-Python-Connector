
class SubActivity(object):
    name = None
    identifier = None
    description = None
    active = True


class Activity(object):
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
        return '<Activity identifier="{}" name="{}" kind="{}"/>'.format(
            self.identifier, self.name, self.kind)


class Name(object):
    family = None
    given = None


class Patient(object):
    uid = None
    name = None

    def __format__(self, _):
        return '<Patient name="{} {}"/>'.format(
            self.name.family, self.name.given)


class Practitioner(object):
    uid = None
    name = None

    def __format__(self, _):
        return '<Practitioner name="{} {}"/>'.format(
            self.name.given, self.name.family)


class CarePlan(object):
    uid = None

    status = None
    patient = None

    def __format__(self, _):
        return '<CarePlan status="{}">{}</CarePlan>'.format(
            self.status,
            self.patient or "<Patient/>")


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
