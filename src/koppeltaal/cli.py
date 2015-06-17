import os
import sys
import argparse
import ConfigParser
import lxml.etree
import logging
import koppeltaal
import koppeltaal.connect
import koppeltaal.create_or_update_care_plan
import koppeltaal.activity_definition


def cli():
    parser = argparse.ArgumentParser(description='Koppeltaal connector')
    parser.add_argument('server', help='Koppeltaal server to connect to')
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--verbose', action='store_true')

    subparsers = parser.add_subparsers(title='commands', dest='command')

    # XXX Inject possible commands here. Some sort of registry.
    subparsers.add_parser('test_authentication')
    subparsers.add_parser('activity_definition')
    subparsers.add_parser('get_next_and_claim')

    message_header = subparsers.add_parser('message_header')
    message_header.add_argument('--patient_id')
    message_header.add_argument('--message_id')

    create_or_update_care_plan = subparsers.add_parser('create_or_update_care_plan')
    create_or_update_care_plan.add_argument('domain')
    create_or_update_care_plan.add_argument('activity_id')
    create_or_update_care_plan.add_argument('patient_id')
    create_or_update_care_plan.add_argument('patient_url')
    create_or_update_care_plan.add_argument('patient_given_name')
    create_or_update_care_plan.add_argument('patient_family_name')
    create_or_update_care_plan.add_argument('careplan_id')
    create_or_update_care_plan.add_argument('careplan_url')
    create_or_update_care_plan.add_argument('practitioner_id')
    create_or_update_care_plan.add_argument('practitioner_url')
    create_or_update_care_plan.add_argument('practitioner_given_name')
    create_or_update_care_plan.add_argument('practitioner_family_name')

    launch = subparsers.add_parser('launch')
    launch.add_argument('activity_id')
    launch.add_argument('patient_url')
    launch.add_argument('user_url')

    args = parser.parse_args()

    root = logging.getLogger()
    root.addHandler(logging.StreamHandler(sys.stdout))

    if args.verbose:
        root.setLevel(logging.DEBUG)

    username = args.username
    password = args.password
    if username is None or password is None:
        parser = ConfigParser.ConfigParser()
        parser.read(os.path.expanduser('~/.koppeltaal.cfg'))
        if not parser.has_section(args.server):
            sys.exit('No user credentials found in ~/.koppeltaal.cfg')
        username = parser.get(args.server, 'username')
        password = parser.get(args.server, 'password')
        if not username or not password:
            sys.exit('No user credentials found in ~/.koppeltaal.cfg')

    connection = koppeltaal.connect.Connector(
        args.server, username, password)

    if args.command == 'test_authentication':
        # Exit code is the opposite of the result from the Connector.
        sys.exit(not connection.test_authentication())
    elif args.command == 'metadata':
        result = connection.metadata()
        print lxml.etree.tostring(lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'activity_definition':
        result = connection.activity_definition()
        print lxml.etree.tostring(lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'message_header':
        result = connection.message_header(
            patient_id=args.patient_id,
            message_id=args.message_id)
        print lxml.etree.tostring(lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'get_next_and_claim':
        result = connection.get_next_and_claim()
        print lxml.etree.tostring(lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'create_or_update_care_plan':
        # XXX Refactor.
        class Name(object):
            given = family = None

        class Patient(object):
            id = url = name = None

            def __init__(self):
                self.name = Name()

        class CarePlan(object):
            id = url = None

        class Practitioner(object):
            id = url = None

            def __init__(self):
                self.name = Name()

        # This will choke on unknown activity ids.
        activity = koppeltaal.activity_definition.activity_info(
            connection.activity_definition(), args.activity_id)

        patient = Patient()
        patient.id = args.patient_id
        patient.url = args.patient_url
        patient.name.given = args.patient_given_name
        patient.name.family = args.patient_family_name

        careplan = CarePlan()
        careplan.id = args.careplan_id
        careplan.url = args.careplan_url

        practitioner = Practitioner()
        practitioner.id = args.practitioner_id
        practitioner.url = args.practitioner_url
        practitioner.name.given = args.practitioner_given_name
        practitioner.name.family = args.practitioner_family_name

        xml = koppeltaal.create_or_update_care_plan.generate(
            args.domain, activity, patient, careplan, practitioner)
        result = connection.create_or_update_care_plan(xml)
        print lxml.etree.tostring(lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'launch':
        # XXX Validate activity-id?
        print connection.launch(args.activity_id, args.patient_url, args.user_url)
    else:
        sys.exit('Unknown command {}'.format(args.command))
