import os
import sys
import json
import argparse
import ConfigParser
import logging

import koppeltaal.connector
import koppeltaal.codes


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
        choices=koppeltaal.codes.PROCESSING_STATUS)

    messages = subparsers.add_parser('messages')
    messages.add_argument(
        '--patient')
    messages.add_argument(
        '--status',
        choices=koppeltaal.codes.PROCESSING_STATUS)
    messages.add_argument(
        '--event',
        choices=koppeltaal.codes.MESSAGE_EVENTS)

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
                event=args.event, status=args.status, patient=args.patient):
            print '{}'.format(message)
    elif args.command == 'message':
        for message in connection.fetch(message_id=args.message_id):
            print '{}'.format(message)
    elif args.command == 'change_messages_status':
        if args.confirm is None:
            print "This is a dry-run."
        num_done = 0
        for message in connection.fetch():
            if message.status == args.status:
                print "Message {} already with the correct status.".format(
                    message.uid)
                continue
            message.status = args.status
            if args.confirm:
                connection.send(message)
                num_done += 1
                if num_done >= args.count:
                    break
            else:
                print "Dry-run: not setting message {} " \
                    "{} to status {}.".format(message.uid, args.status)
        print 'The status of {} messages has been set to "{}".'.format(
            num_done, args.status)
    elif args.command == 'create_or_update_care_plan':
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
        message = koppeltaal.models.Message()
        result = connection.send(message)
    elif args.command == 'launch':
        activity = connection.activity(args.activity_id)

        if activity is None:
            print "Unknown activity {}.".format(args.activity_id)
            return

        activity = koppeltaal.model.Activity(args.activity_id, None, None)
        patient = koppeltaal.models.Patient()
        patient.uid = args.patient_url

        user = koppeltaal.models.Practitioner()
        user.uid = args.user_url
        print connection.launch(activity, patient, user)
    else:
        sys.exit('Unknown command {}'.format(args.command))
