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
    definitions.ActivityDetails: models.ActivityDetails,
    definitions.ActivityParticipant: models.Participant,
    definitions.Address: models.Address,
    definitions.CarePlan: models.CarePlan,
    definitions.CarePlanActivityStatus: models.ActivityStatus,
    definitions.CarePlanSubActivityStatus: models.SubActivity,
    definitions.CareTeam: models.CareTeam,
    definitions.Contact: models.Contact,
    definitions.Goal: models.Goal,
    definitions.Identifier: models.Identifier,
    definitions.Issue: models.Issue,
    definitions.MessageHeader: models.MessageHeader,
    definitions.MessageHeaderResponse: models.MessageHeaderResponse,
    definitions.MessageHeaderSource: models.MessageHeaderSource,
    definitions.Name: models.Name,
    definitions.OperationOutcome: models.OperationOutcome,
    definitions.Organization: models.Organization,
    definitions.OrganizationContactPerson: models.OrganizationContactPerson,
    definitions.Participant: models.Participant,
    definitions.Patient: models.Patient,
    definitions.Period: models.Period,
    definitions.Practitioner: models.Practitioner,
    definitions.ProcessingStatus: models.ProcessingStatus,
    definitions.RelatedPerson: models.RelatedPerson,
    definitions.SubActivity: models.SubActivity,
    definitions.SubActivityDefinition: models.SubActivityDefinition,
})
