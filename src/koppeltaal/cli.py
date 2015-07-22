import os
import sys
import argparse
import ConfigParser
import lxml.etree
import logging
import koppeltaal
import koppeltaal.connect
import koppeltaal.message
import koppeltaal.model
import koppeltaal.create_or_update_care_plan
import koppeltaal.activity_definition


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


def cli():
    parser = argparse.ArgumentParser(description='Koppeltaal connector')
    parser.add_argument('server', help='Koppeltaal server to connect to')
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument(
        '--domain',
        help='The domain on the server to send data to.')
    parser.add_argument('--verbose', action='store_true')

    subparsers = parser.add_subparsers(title='commands', dest='command')

    # XXX Inject possible commands here. Some sort of registry.
    subparsers.add_parser('test_authentication')
    subparsers.add_parser('activity_definition')
    subparsers.add_parser('metadata')

    messages = subparsers.add_parser('messages')
    messages.add_argument('--count')  # How many messages to show.
    messages.add_argument('--patient_url')  # Filter on patient.
    messages.add_argument(
        '--status',
        choices=['New', 'Claimed', 'Success', 'Failed'])
    messages.add_argument('--xml', action='store_true')  # Show xml.
    messages.add_argument('--info_per_message', action='store_true')

    message = subparsers.add_parser('message')
    message.add_argument('id')

    create_or_update_care_plan = subparsers.add_parser(
        'create_or_update_care_plan')
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

    username, password, domain = get_credentials(args)

    connection = koppeltaal.connect.Connector(
        args.server, username, password, domain=domain)

    if args.command == 'test_authentication':
        result = connection.test_authentication()
        print "Authentication successful." if result \
            else "Authentication unsuccessful."
        # Exit code is the opposite of the result from the Connector.
        sys.exit(not result)
    elif args.command == 'metadata':
        result = connection.metadata()
        print lxml.etree.tostring(
            lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'activity_definition':
        result = connection.activity_definition()
        print lxml.etree.tostring(
            lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'messages':
        print "Getting messages... (a slow query)..."
        xml_result = connection.messages(
            count=args.count,
            patient_url=args.patient_url,
            processing_status=args.status,
            summary=True)
        messages = list(koppeltaal.message.parse_messages(xml_result))
        if args.info_per_message:
            for msg in messages:
                print msg.id, msg.status
        if args.xml:
            print lxml.etree.tostring(
                lxml.etree.fromstring(xml_result), pretty_print=True)
        print "Number of messages found: {}.".format(len(messages))
    elif args.command == 'message':
        import pdb
        pdb.set_trace()
    elif args.command == 'create_or_update_care_plan':
        # This will choke on unknown activity ids.
        activity = koppeltaal.activity_definition.activity_info(
            connection.activity_definition(), args.activity_id)

        patient = koppeltaal.model.Patient(args.patient_id, args.patient_url)
        patient.name.given = args.patient_given_name
        patient.name.family = args.patient_family_name

        careplan = koppeltaal.model.CarePlan(
            args.careplan_id, args.careplan_url, patient)

        practitioner = koppeltaal.model.Practitioner(
            args.practitioner_id, args.practitioner_url)
        practitioner.name.given = args.practitioner_given_name
        practitioner.name.family = args.practitioner_family_name

        xml = koppeltaal.create_or_update_care_plan.generate(
            connection.domain, activity, patient, careplan, practitioner)
        result = connection.post_message(xml)
        print lxml.etree.tostring(
            lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'launch':
        # XXX Validate activity-id?
        print connection.launch(
            args.activity_id, args.patient_url, args.user_url)
    else:
        sys.exit('Unknown command {}'.format(args.command))
