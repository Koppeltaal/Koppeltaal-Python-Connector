import os
import sys
import json
import argparse
import ConfigParser
import lxml.etree
import logging
import koppeltaal
import koppeltaal.activity_definition
import koppeltaal.configuration
import koppeltaal.connect
import koppeltaal.create_or_update_care_plan
import koppeltaal.feed
import koppeltaal.model

import koppeltaal.connector


def pretty_print(data):
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


def cli():
    # URLs to the patient and practitioner, and other objects are provided on
    # the command line and thus as not to be computed. We configure the URL
    # computation hook so that is takes the URL from an annotation on the
    # objects that we createed here.
    def annotated_url(context):
        return context.__url__

    koppeltaal.configuration.set_url_function(annotated_url)

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
    subparsers.add_parser('activities')
    subparsers.add_parser('metadata')

    change_messages_status = subparsers.add_parser('change_messages_status')
    change_messages_status.add_argument('--count', type=int, default=100)
    change_messages_status.add_argument('--confirm', action='store_true')
    change_messages_status.add_argument(
        '--status',
        choices=['New', 'Claimed', 'Success', 'Failed'])

    messages = subparsers.add_parser('messages')
    messages.add_argument('--count')  # How many messages to show.
    messages.add_argument('--patient_url')  # Filter on patient.
    messages.add_argument(
        '--status',
        choices=['New', 'Claimed', 'Success', 'Failed'])
    messages.add_argument(
        '--event',
        choices=['CreateOrUpdateCarePlan', 'UpdateCarePlanActivityStatus'])

    message = subparsers.add_parser('message')
    message.add_argument('message_id')

    create_or_update_care_plan = subparsers.add_parser(
        'create_or_update_care_plan')
    create_or_update_care_plan.add_argument('activity_id')
    create_or_update_care_plan.add_argument('patient_url')
    create_or_update_care_plan.add_argument('patient_given_name')
    create_or_update_care_plan.add_argument('patient_family_name')
    create_or_update_care_plan.add_argument('careplan_url')
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

    connection = koppeltaal.connector.Connector(
        args.server, username, password, domain=domain)

    if args.command == 'test_authentication':
        result = connection.test_authentication()
        print "Authentication successful." if result \
            else "Authentication unsuccessful."
        # Exit code is the opposite of the result from the Connector.
        sys.exit(not result)
    elif args.command == 'metadata':
        pretty_print(connection.metadata())
    elif args.command == 'activities':
        for activity in connection.activities():
            print '{}'.format(activity)
    elif args.command == 'messages':
        for message in connection.fetch(
                event=args.event, status=args.status, count=args.count):
            print '{}'.format(message)
    elif args.command == 'message':
        for message in connection.fetch(
                message_id=args.message_id):
            print '{}'.format(message)
    elif args.command == 'change_messages_status':
        if args.confirm is None:
            print "This is a dry-run."
        num_done = 0
        for msg in list(koppeltaal.feed.parse(
                connection.messages(summary=True))):
            if msg.status != args.status:
                if args.confirm:
                    connection._process_message(
                        msg.__version__, status=args.status)
                else:
                    print "Dry-run: not setting message with message id " \
                        "{} to status {}.".format(msg.__version__, args.status)
            num_done += 1
            if num_done >= args.count:
                break
        print 'The status of {} messages has been set to "{}".'.format(
            num_done, args.status)
    elif args.command == 'create_or_update_care_plan':
        activity = koppeltaal.activity_definition.activity_info(
            connection.activity_definition(), args.activity_id)

        patient = koppeltaal.model.Patient()
        patient.__url__ = args.patient_url
        patient.name.given = args.patient_given_name
        patient.name.family = args.patient_family_name

        practitioner = koppeltaal.model.Practitioner()
        practitioner.__url__ = args.practitioner_url
        practitioner.name.given = args.practitioner_given_name
        practitioner.name.family = args.practitioner_family_name

        careplan = koppeltaal.model.CarePlan(patient)
        xml = koppeltaal.create_or_update_care_plan.generate(
            connection.domain, activity, careplan, practitioner)
        result = connection.post_message(xml)
        print lxml.etree.tostring(
            lxml.etree.fromstring(result), pretty_print=True)
    elif args.command == 'launch':
        activity = koppeltaal.model.Activity(args.activity_id, None, None)
        patient = koppeltaal.model.Patient()
        patient.__url__ - args.patient_url

        user = koppeltaal.model.Practitioner()
        user.__url__ = args.user_url
        # XXX Validate activity-id?
        print connection.launch(activity, patient, user)
    else:
        sys.exit('Unknown command {}'.format(args.command))
