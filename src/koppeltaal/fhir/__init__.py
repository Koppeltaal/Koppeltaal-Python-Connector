# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

from koppeltaal.fhir.registry import Registry
from koppeltaal import definitions, models


REGISTRY = Registry({
    definitions.Activity: models.Activity,
    definitions.ActivityDefinition: models.ActivityDefinition,
    definitions.ActivityParticipant: models.Participant,
    definitions.CarePlan: models.CarePlan,
    definitions.CarePlanActivityStatus: models.ActivityStatus,
    definitions.CarePlanSubActivityStatus: models.SubActivity,
    definitions.Contact: models.Contact,
    definitions.Goal: models.Goal,
    definitions.Identifier: models.Identifier,
    definitions.MessageHeader: models.MessageHeader,
    definitions.MessageHeaderResponse: models.MessageHeaderResponse,
    definitions.MessageHeaderSource: models.MessageHeaderSource,
    definitions.Name: models.Name,
    definitions.Organization: models.Organization,
    definitions.OrganizationContactPerson: models.OrganizationContactPerson,
    definitions.Participant: models.Participant,
    definitions.Patient: models.Patient,
    definitions.Practitioner: models.Practitioner,
    definitions.ProcessingStatus: models.Status,
    definitions.SubActivity: models.SubActivity,
    definitions.SubActivityDefinition: models.SubActivityDefinition,
})
