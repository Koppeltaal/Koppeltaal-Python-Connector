import ConfigParser
import argparse
import json
import logging
import os
import pdb
import sys
import dateutil

from koppeltaal import (connector, codes, models, utils)
from koppeltaal.fhir import xml, bundle


ACTIVITY_DEFINITION_OUTPUT = """Activity: {model.identifier}
- fhir link: {model.fhir_link}
- name: {model.name}
- description: {model.description}
- kind: {model.kind}
- performer: {model.performer}
- active: {model.is_active}
- domain specific: {model.is_domain_specific}
- archived: {model.is_archived}
"""

ACTIVITY_STATUS_OUTPUT = """Activity Status: {model.identifier}
- fhir link: {model.fhir_link}
- status: {model.status}
"""

MESSAGE_OUTPUT = """Message: {model.identifier}
- fhir link: {model.fhir_link}
- event: {model.event}
- time stamp: {model.timestamp}
"""

CAREPLAN_OUTPUT = """CarePlan:
- fhir link: {model.fhir_link}
"""

PATIENT_OUTPUT = """Patient: {model.name.family} {model.name.given}
- fhir link: {model.fhir_link}
"""

PRACTITIONER_OUTPUT = """Practitioner: {model.name.family} {model.name.given}
- fhir link: {model.fhir_link}
"""

OUTPUT = {
    models.ActivityDefinition: ACTIVITY_DEFINITION_OUTPUT,
    models.ActivityStatus: ACTIVITY_STATUS_OUTPUT,
    models.CarePlan: CAREPLAN_OUTPUT,
    models.MessageHeader: MESSAGE_OUTPUT,
    models.Patient: PATIENT_OUTPUT,
    models.Practitioner: PRACTITIONER_OUTPUT,
}


def print_model(model):
    output = OUTPUT.get(model.__class__)
    if output:
        print output.format(model=model)


def print_json(data):
    print json.dumps(data, indent=2, sort_keys=True)


def get_credentials(args):
    # Domain is not required for all actions, so we're less strict about
    # requiring that.
    if args.username or args.password or args.domain:
        if not(args.username and args.password):
            sys.exit(
                'When supplying credentials through the commandline '
                'please always supply username and password.')
        else:
            return args.username, args.password, args.domain

    # They're not passed in, so now look at ~/.koppeltaal.cfg.
    parser = ConfigParser.ConfigParser()
    parser.read(os.path.expanduser('~/.koppeltaal.cfg'))
    if not parser.has_section(args.server):
        sys.exit('No user credentials found in ~/.koppeltaal.cfg')
    username = parser.get(args.server, 'username')
    password = parser.get(args.server, 'password')
    # Domain is not required for all actions.
    domain = parser.get(args.server, 'domain')
    if not username or not password:
        sys.exit('No user credentials found in ~/.koppeltaal.cfg')
    return username, password, domain


class DummyResource(object):

    def __new__(cls, fhir_link):
        if fhir_link is None:
            return None
        return object.__new__(cls, fhir_link)

    def __init__(self, fhir_link):
        self.fhir_link = fhir_link


def cli():
    parser = argparse.ArgumentParser(description='Koppeltaal connector')
    parser.add_argument('server', help='Koppeltaal server to connect to')
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument(
        '--domain',
        help='The domain on the server to send data to')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument(
        '--post-mortem',
        action='store_true',
        help='Debug any error with a Python debugger')

    subparsers = parser.add_subparsers(title='commands', dest='command')

    subparsers.add_parser('activities')
    subparsers.add_parser('metadata')

    validate = subparsers.add_parser('validate')
    validate.add_argument(
        '--xml', type=argparse.FileType('rb'),
        help="XML file to validate")
    validate.add_argument(
        '--json', type=argparse.FileType('rb'),
        help="JSON file to validate")

    messages = subparsers.add_parser('messages')
    messages.add_argument(
        '--patient',
        help='Patient FHIR link')
    messages.add_argument(
        '--status',
        choices=codes.PROCESSING_STATUS,
        help='Message header status')
    messages.add_argument(
        '--event', choices=codes.MESSAGE_HEADER_EVENTS,
        help='Event type')

    message = subparsers.add_parser('message')
    message.add_argument('message_id')

    updates = subparsers.add_parser('updates')
    updates.add_argument(
        '--until',
        help='Process all next messages until the given date (and time)')
    updates.add_argument(
        '--failure',
        help='Fail and set the exception on the messages.')

    care_plan = subparsers.add_parser('care_plan')
    care_plan.add_argument('activity_id')
    care_plan.add_argument('patient_url')
    care_plan.add_argument('patient_given_name')
    care_plan.add_argument('patient_family_name')
    care_plan.add_argument('careplan_url')
    care_plan.add_argument('practitioner_url')
    care_plan.add_argument('practitioner_given_name')
    care_plan.add_argument('practitioner_family_name')

    launch = subparsers.add_parser('launch')
    launch.add_argument(
        '--activity', required=True,
        help='Activity identifier')
    launch.add_argument(
        '--patient', required=True,
        help='Patient FHIR link')
    launch.add_argument(
        '--user', required=True,
        help='FHIR link of the user launching the activity')

    args = parser.parse_args()

    root = logging.getLogger()
    root.addHandler(logging.StreamHandler(sys.stdout))

    if args.verbose:
        root.setLevel(logging.DEBUG)

    username, password, domain = get_credentials(args)

    configuration = connector.FHIRConfiguration(name='Python command line')
    connection = connector.Connector(
        args.server, username, password, domain, configuration)

    try:
        if args.command == 'metadata':
            print_json(connection.metadata())
        elif args.command == 'validate':
            payload = None
            if args.xml:
                payload = xml.xml2json(args.xml)
            if args.json:
                payload = json.load(args.json)
            if payload is None:
                print "Please provide an XML or JSON file."
                return
            print_json(payload)
            resource_bundle = bundle.Bundle(domain, configuration)
            resource_bundle.add_payload(payload)
            for model in resource_bundle.unpack():
                print_model(model)
        elif args.command == 'activities':
            for activity in connection.activities():
                print_model(activity)
        elif args.command == 'messages':
            for message in connection.search(
                    event=args.event,
                    status=args.status,
                    patient=DummyResource(args.patient)):
                print_model(message)
        elif args.command == 'message':
            for model in connection.search(message_id=args.message_id):
                print_model(model)
        elif args.command == 'care_plan':
            activity = connection.activity(args.activity_id)

            if activity is None:
                print "Unknown activity {}.".format(args.activity_id)
                return

            # patient = koppeltaal.model.Patient()
            # patient.__url__ = args.patient_url
            # patient.name.given = args.patient_given_name
            # patient.name.family = args.patient_family_name

            # practitioner = koppeltaal.model.Practitioner()
            # practitioner.__url__ = args.practitioner_url
            # practitioner.name.given = args.practitioner_given_name
            # practitioner.name.family = args.practitioner_family_name

            # careplan = koppeltaal.models.CarePlan()
            message = models.Message()
            print_json(connection.send(message))
        elif args.command == 'updates':
            until = None
            if args.until is not None:
                until = dateutil.parser.parse(args.until, tzinfos=utils.UTC)

            for index, update in enumerate(connection.updates()):
                with update:
                    if until is None:
                        if index:
                            update.postpone()
                            break
                    else:
                        if update.message.timestamp > until:
                            update.postpone()
                            break
                    print_model(update.data)
                    if args.failure:
                        update.fail(args.failure)

        elif args.command == 'launch':
            activity = connection.activity(args.activity)

            if activity is None:
                print "Unknown activity {}.".format(args.activity)
                return

            patient = DummyResource(args.patient)
            user = DummyResource(args.user)
            print connection.launch(activity, patient, user)
        else:
            sys.exit('Unknown command {}'.format(args.command))
    except Exception as error:
        if args.post_mortem:
            print error
            pdb.post_mortem()
        raise
