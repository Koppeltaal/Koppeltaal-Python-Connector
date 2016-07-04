
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


class Patient(object):

    def __init__(self, uid, family_name, given_name):
        self.uid = uid
        self.family_name = family_name
        self.given_name = given_name

    def __format__(self, _):
        return '<Patient name="{} {}"/>'.format(
            self.given_name, self.family_name)


class Practitioner(object):

    def __init__(self, uid, family_name, given_name):
        self.uid = uid
        self.family_name = family_name
        self.given_name = given_name

    def __format__(self, _):
        return '<Practitioner name="{} {}"/>'.format(
            self.given_name, self.family_name)


class CarePlan(object):
    patient = None

    def __init__(self, uid):
        self.uid = uid


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
                '{}</Message>').format(
                    self.event,
                    self.status.status,
                    self.status.last_changed,
                    self.patient or "<Patient/>")
