"""
Helpers for the CreateOrUpdateCarePlan Message.

This creates a atom feed to send to the server.
"""
import uuid
import datetime
import feedgen.feed
import feedreader.parser
import lxml.etree
import koppeltaal
import koppeltaal.model
import koppeltaal_schema.validate


def generate(domain, activity, patient, careplan, practitioner):
    '''
    activity is an info dict as defined by koppeltaal.activity_definition

    patient is an object with information about the patient:
      id
      url
      name = object with attributes 'given' and 'family'

    careplan is an object with information about the careplan:
      id
      url
      # add active flag?

    practitioner is an object with information about the practitioner:
      id
      url
      name = object with attributes 'given' and 'family'
    '''
    assert domain
    now = datetime.datetime.utcnow().isoformat()

    # Create the feed envelope.
    feed = feedgen.feed.FeedGenerator()
    # No thanks, this chokes the validation of the message.
    feed._FeedGenerator__atom_generator = None
    # Set a title and id, required field for feedgen.
    feed_id = str(uuid.uuid4())
    feed.id(feed_id)
    feed.title('Feed with id {}'.format(feed_id))
    # Required Koppeltaal elements.
    feed.category(
        term='{koppeltaal}/Domain#{domain}'.format(
            domain=domain, **koppeltaal.NS),
        label=domain,
        scheme='{fhir}/tag/security'.format(**koppeltaal.NS))
    feed.category(
        term='{fhir}/tag/message'.format(**koppeltaal.NS),
        scheme='{fhir}/tag'.format(**koppeltaal.NS))

    # first, the message header.
    messageheader_entry = feed.add_entry()
    message_id = str(uuid.uuid4())
    # Please feedgen with a id and title.
    messageheader_entry.id(message_id)
    messageheader_entry.title(
        'MessageHeader resource with id {}'.format(message_id))
    messageheader = lxml.etree.Element(
        'MessageHeader',
        nsmap={None: koppeltaal.NS['fhir']})
    extension = lxml.etree.SubElement(
        messageheader,
        'extension',
        attrib={
            'url': '{koppeltaal}/MessageHeader#Patient'.format(**koppeltaal.NS)
        })
    valueResource = lxml.etree.SubElement(extension, 'valueResource')
    lxml.etree.SubElement(valueResource, 'reference', attrib={
        'value': patient.url
        })
    lxml.etree.SubElement(messageheader, 'identifier', attrib={
        'value': message_id})
    lxml.etree.SubElement(messageheader, 'timestamp', attrib={
        'value': now})
    event = lxml.etree.SubElement(messageheader, 'event')
    lxml.etree.SubElement(event, 'system', attrib={
        'value': '{koppeltaal}/MessageEvents'.format(**koppeltaal.NS)
    })
    lxml.etree.SubElement(event, 'code', attrib={
        'value': 'CreateOrUpdateCarePlan'
    })
    lxml.etree.SubElement(event, 'display', attrib={
        'value': 'CreateOrUpdateCarePlan'
    })
    source = lxml.etree.SubElement(messageheader, 'source')
    # XXX Get info about this package from setup tools here.
    lxml.etree.SubElement(source, 'software', attrib={
        'value': 'Whatever'
    })
    lxml.etree.SubElement(source, 'endpoint', attrib={
        'value': 'SomeStuff'
    })
    data = lxml.etree.SubElement(messageheader, 'data')
    lxml.etree.SubElement(data, 'reference', attrib={'value': careplan.url})

    # Add message header to feed.
    messageheader_entry.content(
        lxml.etree.tostring(messageheader), type='text/xml')

    # And now for my next trick, a CarePlan!
    careplan_entry = feed.add_entry()
    # Please feedgen with a id and title.
    careplan_entry.id(careplan.id)
    careplan_entry.title('CarePlan resource with id {}'.format(careplan.id))
    careplan_entry.link(rel='self', href=careplan.url)

    careplan_el = lxml.etree.Element(
        'CarePlan',
        attrib={'id': careplan.id},
        nsmap={None: koppeltaal.NS['fhir']})

    patient_el = lxml.etree.SubElement(careplan_el, 'patient')
    lxml.etree.SubElement(
        patient_el, 'reference', attrib={'value': patient.url})
    lxml.etree.SubElement(careplan_el, 'status', attrib={'value': 'active'})
    participant = lxml.etree.SubElement(careplan_el, 'participant')
    role = lxml.etree.SubElement(participant, 'role')
    coding = lxml.etree.SubElement(role, 'coding')
    lxml.etree.SubElement(coding, 'system', attrib={
        'value':
        '{koppeltaal}/CarePlanParticipantRole'.format(**koppeltaal.NS)
    })
    lxml.etree.SubElement(coding, 'code', attrib={'value': 'Requester'})
    lxml.etree.SubElement(coding, 'display', attrib={'value': 'Requester'})
    member = lxml.etree.SubElement(participant, 'member')
    lxml.etree.SubElement(
        member, 'reference', attrib={'value': practitioner.url})

    # goal
    # goal id doesn't seem to be part of the schema validation.
    goal = lxml.etree.SubElement(careplan_el, 'goal')
    lxml.etree.SubElement(goal, 'description', attrib={'value': '-'})
    lxml.etree.SubElement(goal, 'status', attrib={'value': 'in progress'})

    # activity
    activity_el = lxml.etree.SubElement(careplan_el, 'activity')
    activity_definition = lxml.etree.SubElement(
        activity_el,
        'extension',
        attrib={
            'url': '{koppeltaal}/CarePlan#ActivityDefinition'.format(
                **koppeltaal.NS)
        })
    lxml.etree.SubElement(
        activity_definition, 'valueString', attrib={'value': activity.id})

    activity_kind = lxml.etree.SubElement(
        activity_el,
        'extension',
        attrib={
            'url': '{koppeltaal}/CarePlan#ActivityKind'.format(**koppeltaal.NS)
        }
    )
    value_coding = lxml.etree.SubElement(activity_kind, 'valueCoding')
    lxml.etree.SubElement(value_coding, 'system', attrib={
        'value': '{koppeltaal}/ActivityKind'.format(**koppeltaal.NS)
    })
    # From activity kind information.
    lxml.etree.SubElement(value_coding, 'code', attrib={
        'value': activity.kind['code']
    })
    lxml.etree.SubElement(value_coding, 'display', attrib={
        'value': activity.kind['display']
    })
    # prohibited is required by the schema.
    lxml.etree.SubElement(activity_el, 'prohibited', attrib={'value': 'false'})

    careplan_entry.content(lxml.etree.tostring(careplan_el), type='text/xml')

    # Add Patient entry.
    patient_entry = feed.add_entry()
    patient_entry.id(patient.id)
    patient_entry.title('Patient resource with id {}'.format(patient.id))
    patient_entry.link(rel='self', href=patient.url)

    # Add patient age and gender?
    patient_entry_el = lxml.etree.Element(
        'Patient',
        attrib={'id': patient.id},
        nsmap={None: koppeltaal.NS['fhir']})
    patient_name = lxml.etree.SubElement(patient_entry_el, 'name')
    lxml.etree.SubElement(patient_name, 'use', attrib={'value': 'official'})
    lxml.etree.SubElement(patient_name, 'family', attrib={
        'value': patient.name.family})
    lxml.etree.SubElement(patient_name, 'given', attrib={
        'value': patient.name.given})
    patient_entry.content(
        lxml.etree.tostring(patient_entry_el), type='text/xml')

    # Add Practitioner entry.
    practitioner_entry = feed.add_entry()
    practitioner_entry.id(practitioner.id)
    practitioner_entry.title(
        'Practitioner resource with id {}'.format(practitioner.id))
    practitioner_entry.link(rel='self', href=practitioner.url)

    practitioner_entry_el = lxml.etree.Element(
        'Practitioner',
        attrib={'id': practitioner.id},
        nsmap={None: koppeltaal.NS['fhir']})
    practitioner_name = lxml.etree.SubElement(practitioner_entry_el, 'name')
    lxml.etree.SubElement(
        practitioner_name, 'use', attrib={'value': 'official'})
    lxml.etree.SubElement(practitioner_name, 'family', attrib={
        'value': practitioner.name.family})
    lxml.etree.SubElement(practitioner_name, 'given', attrib={
        'value': practitioner.name.given})
    practitioner_entry.content(
        lxml.etree.tostring(practitioner_entry_el), type='text/xml')

    feed_str = feed.atom_str(pretty=True)
    # XXX Move the logging to the validation code.
    try:
        koppeltaal_schema.validate.validate(lxml.etree.fromstring(feed_str))
    except koppeltaal_schema.validate.ValidationError as err:
        koppeltaal.logger.error(
            'validation error: {} for message {}'.format(
                err.message, feed_str))
        raise
    return feed_str


def parse_result(xml):
    # Perhaps refactor this to use koppeltaal.feed.
    feed = feedreader.parser.from_string(xml)
    reference = feed.entries[0].content.find(
        'fhir:MessageHeader', namespaces=koppeltaal.NS).find(
        'fhir:data', namespaces=koppeltaal.NS).find(
        'fhir:reference', namespaces=koppeltaal.NS).get('value')
    return koppeltaal.model.CarePlanResult(reference)
