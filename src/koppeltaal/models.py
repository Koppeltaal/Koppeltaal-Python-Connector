

class Activity(object):

    def __init__(
            self, uid, identifier, kind, name,
            performer="Patient", active=True,
            domain_specific=False, launch_type="Web", archived=False):
        self.uid = uid
        self.identifier = identifier
        self.name = name
        self.kind = kind
        self.performer = performer
        self.active = active
        self.domain_specific = domain_specific
        self.launch_type = launch_type
        self.archived = archived

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

    def __init__(self, uid, patient):
        self.uid = uid
        self.patient = patient


class Message(object):

    def __init__(
            self, uid, message_type, status, last_changed,
            patient=None, data=None):
        self.uid = uid
        self.message_type = message_type
        self.status = status
        self.last_changed = last_changed
        self.patient = patient
        self.data = data

    def __format__(self, _):
        return '<Message type="{}" status="{}" last_changed"{}"/>'.format(
            self.message_type, self.status, self.last_changed)
