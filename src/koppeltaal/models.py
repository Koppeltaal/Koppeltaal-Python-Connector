# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import zope.interface

from koppeltaal import (definitions, interfaces)


@zope.interface.implementer(interfaces.IFHIRResource)
class FHIRResource(object):
    fhir_link = None


@zope.interface.implementer(interfaces.IReferredFHIRResource)
class ReferredResource(FHIRResource):
    display = None

    def __init__(self, fhir_link=None, display=None):
        self.fhir_link = fhir_link
        self.display = display


@zope.interface.implementer(definitions.SubActivityDefinition)
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


@zope.interface.implementer(definitions.ActivityDefinition)
class ActivityDefinition(FHIRResource):

    def __init__(
            self,
            description=None,
            identifier=None,
            application=None,
            is_active=True,
            is_archived=False,
            is_domain_specific=False,
            kind=None,
            launch_type='Web',
            name=None,
            performer=None,
            subactivities=None):
        self.description = description
        self.identifier = identifier
        self.application = application
        self.is_active = is_active
        self.is_archived = is_archived
        self.is_domain_specific = is_domain_specific
        self.kind = kind
        self.launch_type = launch_type
        self.name = name
        self.performer = performer
        self.subactivities = subactivities


@zope.interface.implementer(definitions.Name)
class Name(object):

    def __init__(
            self,
            family=None,
            given=None,
            prefix=None,
            suffix=None,
            text=None,
            use="official"):
        self.family = family
        self.given = given
        self.prefix = prefix
        self.suffix = suffix
        self.text = text
        self.use = use


@zope.interface.implementer(definitions.Contact)
class Contact(object):

    def __init__(
            self,
            system=None,
            value=None,
            use=None):
        self.system = system
        self.value = value
        self.use = use


@zope.interface.implementer(definitions.Identifier)
class Identifier(object):

    def __init__(
            self,
            system=None,
            value=None,
            use=None):
        self.system = system
        self.value = value
        self.use = use


@zope.interface.implementer(definitions.Participant)
@zope.interface.implementer(definitions.ActivityParticipant)
class Participant(object):

    def __init__(
            self,
            member=None,
            role=None,
            careteam=None):
        self.member = member
        self.role = role
        self.careteam = careteam


@zope.interface.implementer(definitions.OrganizationContactPerson)
class OrganizationContactPerson(object):

    def __init__(
            self,
            contacts=None,
            gender=None,
            name=None,
            purpose=None):
        self.contacts = contacts
        self.gender = gender
        self.name = name
        self.purpose = purpose


@zope.interface.implementer(definitions.Organization)
class Organization(FHIRResource):

    def __init__(
            self,
            active=None,
            address=None,
            category=None,
            contacts=None,
            contact_persons=None,
            identifiers=None,
            name=None,
            part_of=None):
        self.active = active
        self.address = address
        self.category = category
        self.contacts = contacts
        self.contact_persons = contact_persons
        self.identifiers = identifiers
        self.name = name
        self.part_of = part_of


@zope.interface.implementer(definitions.Patient)
class Patient(FHIRResource):

    def __init__(
            self,
            active=None,
            address=None,
            age=None,
            birth_date=None,
            care_providers=None,
            contacts=None,
            identifiers=None,
            gender=None,
            name=None,
            managing_organization=None):
        self.active = active
        self.address = address
        self.age = age
        self.birth_date = birth_date
        self.care_providers = care_providers
        self.contacts = contacts
        self.identifiers = identifiers
        self.gender = gender
        self.name = name
        self.managing_organization = managing_organization


@zope.interface.implementer(definitions.Practitioner)
class Practitioner(FHIRResource):

    def __init__(
            self,
            birth_date=None,
            contacts=None,
            identifiers=None,
            name=None,
            gender=None,
            organization=None):
        self.birth_date = birth_date
        self.contacts = contacts
        self.identifiers = identifiers
        self.name = name
        self.gender = gender
        self.organization = organization


@zope.interface.implementer(definitions.RelatedPerson)
class RelatedPerson(FHIRResource):

    def __init__(
            self,
            identifiers=None,
            patient=None,
            relationship=None,
            name=None,
            contacts=None,
            gender=None,
            address=None,
            photo=None):
        self.identifiers = identifiers
        self.patient = patient
        self.relationship = relationship
        self.name = name
        self.contacts = contacts
        self.gender = gender
        self.address = address
        self.photo = photo


@zope.interface.implementer(definitions.Goal)
class Goal(object):

    def __init__(
            self,
            description=None,
            notes=None,
            status=None):
        self.description = description
        self.status = status
        self.notes = notes


@zope.interface.implementer(definitions.CarePlanSubActivityStatus)
@zope.interface.implementer(definitions.SubActivity)
class SubActivity(object):

    def __init__(
            self,
            definition=None,
            status=None):
        self.definition = definition
        self.status = status


@zope.interface.implementer(definitions.ActivityDetails)
class ActivityDetails(object):

    def __init__(
            self,
            category=None,
            performers=None):
        self.category = category
        self.performers = performers


@zope.interface.implementer(definitions.Activity)
class Activity(object):

    def __init__(
            self,
            cancelled=None,
            definition=None,
            description=None,
            ends=None,
            finished=None,
            identifier=None,
            kind=None,
            notes=None,
            participants=None,
            planned=None,
            started=None,
            status=None,
            subactivities=None,
            details=None,
            prohibited=False):
        self.cancelled = cancelled
        self.definition = definition
        self.description = description
        self.finished = finished
        self.ends = ends
        self.identifier = identifier
        self.kind = kind
        self.notes = notes
        self.participants = participants
        self.planned = planned
        self.started = started
        self.status = status
        self.subactivities = subactivities
        self.details = details
        self.prohibited = prohibited


@zope.interface.implementer(definitions.CarePlan)
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


@zope.interface.implementer(definitions.ProcessingStatus)
class ProcessingStatus(object):

    def __init__(
            self,
            exception=None,
            last_changed=None,
            status=None):
        self.exception = exception
        self.last_changed = last_changed
        self.status = status


@zope.interface.implementer(definitions.CarePlanActivityStatus)
class ActivityStatus(FHIRResource):

    def __init__(
            self,
            identifier=None,
            status=None,
            subactivities=None,
            percentage=None):
        self.identifier = identifier
        self.status = status
        self.subactivities = subactivities
        self.percentage = percentage


@zope.interface.implementer(definitions.MessageHeaderResponse)
class MessageHeaderResponse(object):

    def __init__(self,
                 identifier=None,
                 code=None):
        self.identifier = identifier
        self.code = code


@zope.interface.implementer(definitions.MessageHeaderSource)
class MessageHeaderSource(object):

    def __init__(
            self,
            endpoint=None,
            name=None,
            software=None,
            version=None):
        self.endpoint = endpoint
        self.name = name
        self.software = software
        self.version = version


@zope.interface.implementer(definitions.MessageHeader)
class MessageHeader(FHIRResource):

    def __init__(
            self,
            data=None,
            event=None,
            identifier=None,
            patient=None,
            response=None,
            source=None,
            status=None,
            timestamp=None):
        self.data = data
        self.event = event
        self.identifier = identifier
        self.patient = patient
        self.response = response
        self.source = source
        self.status = status
        self.timestamp = timestamp


@zope.interface.implementer(definitions.Period)
class Period(object):

    def __init__(
            self,
            start=None,
            end=None):
        self.start = start
        self.end = end


@zope.interface.implementer(definitions.CareTeam)
class CareTeam(FHIRResource):

    def __init__(
            self,
            identifier=None,
            status=None,
            name=None,
            subject=None,
            period=None,
            managing_organization=None):
        self.identifier = identifier
        self.status = status
        self.name = name
        self.subject = subject
        self.period = period
        self.managing_organization = managing_organization


@zope.interface.implementer(definitions.Address)
class Address(object):

    def __init__(
            self,
            city=None,
            country=None,
            line=None,
            period=None,
            state=None,
            text=None,
            use=None,
            zip=None):
        self.city = city
        self.country = country
        self.line = line
        self.period = period
        self.state = state
        self.text = text
        self.use = use
        self.zip = zip


@zope.interface.implementer(definitions.Issue)
class Issue(object):

    def __init__(
            self,
            severity=None,
            type=None,
            resource=None,
            details=None,
            location=None):
        self.severity = severity
        self.type = type
        self.resource = resource
        self.details = details
        self.location = location


@zope.interface.implementer(definitions.OperationOutcome)
class OperationOutcome(FHIRResource):

    def __init__(
            self,
            issue=None):
        self.issue = issue
