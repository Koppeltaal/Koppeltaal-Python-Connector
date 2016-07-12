
from koppeltaal.fhir.registry import Registry
from koppeltaal import definitions, models


REGISTRY = Registry({
    definitions.Activity: models.Activity,
    definitions.ActivityDefinition: models.ActivityDefinition,
    definitions.ActivityParticipant: models.Participant,
    definitions.CarePlan: models.CarePlan,
    definitions.Goal: models.Goal,
    definitions.MessageHeader: models.MessageHeader,
    definitions.Name: models.Name,
    definitions.Participant: models.Participant,
    definitions.Patient: models.Patient,
    definitions.Practitioner: models.Practitioner,
    definitions.ProcessingStatus: models.Status,
    definitions.Source: models.Source,
    definitions.SubActivity: models.SubActivity,
    definitions.SubActivityDefinition: models.SubActivityDefinition,
})
