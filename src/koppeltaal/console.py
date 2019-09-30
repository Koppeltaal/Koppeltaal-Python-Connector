# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import argparse
import json
import logging
import os
import os.path
import pdb
import sys
import dateutil

from koppeltaal import connector, codes, definitions, interfaces
from koppeltaal import models, logger, utils
from koppeltaal.fhir import xml, bundle


ACTIVITY_DEFINITION_OUTPUT = """Activity: {model.identifier}
- fhir link: {model.fhir_link}
- active: {model.is_active}
- application: {model.application.fhir_link}
- archived: {model.is_archived}
- description: {model.description}
- domain specific: {model.is_domain_specific}
- kind: {model.kind}
- name: {model.name}
- performer: {model.performer}
"""

ACTIVITY_STATUS_OUTPUT = """Activity Status: {model.identifier}
- fhir link: {model.fhir_link}
- status: {model.status}
"""

MESSAGE_OUTPUT = """Message: {model.identifier}
- fhir link: {model.fhir_link}
- event: {model.event}
- time stamp: {model.timestamp}
- software: {model.source.software} ({model.source.version})
- endpoint: {model.source.endpoint}
"""

CAREPLAN_OUTPUT = """CarePlan:
- fhir link: {model.fhir_link}
"""

PATIENT_OUTPUT = """Patient: {model.name}
- fhir link: {model.fhir_link}
"""

PRACTITIONER_OUTPUT = """Practitioner: {model.name}
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
        print(output.format(model=model))
    else:
        print(model)


def print_json(data):
    print(json.dumps(data, indent=2, sort_keys=True))


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
    return utils.get_credentials_from_file(args.server)


class DummyResource(object):

    def __new__(cls, fhir_link):
        if fhir_link is None:
            return None
        return object.__new__(cls)

    def __init__(self, fhir_link):
        self.fhir_link = fhir_link


def directory(input):
    directory_name = os.path.abspath(os.path.expanduser(input))
    if not os.path.exists(directory_name):
        sys.exit(
            '"{}" does not exist'.format(input))
    if not os.path.isdir(directory_name):
        sys.exit(
            '"{}" is not a valid directory path'.format(input))
    return directory_name


def download(connection, directory, msgid=None, msg=None):
    if msg is not None:
        url = utils.strip_history_from_link(msg.fhir_link)
        msgid = url.rsplit('/', 1)[-1]
    response = connection.transport.query(
        interfaces.MESSAGE_HEADER_URL, {'_id': msgid}).json
    packaging = bundle.Bundle(connection.domain, connection.integration)
    packaging.add_payload(response)
    msg = packaging.unpack_model(definitions.MessageHeader)
    ts = msg.timestamp.isoformat()
    directory = os.path.join(directory, connection.domain)
    if not os.path.exists(directory):
        os.mkdir(directory)
    filename = os.path.join(directory, '{}-{}.json'.format(ts, msgid))
    with open(filename, 'w') as output:
        json.dump(
            response,
            output,
            indent=2,
            sort_keys=True)
    print('Wrote message "{}" to "{}"'.format(msgid, filename))


def _metadata(args, connection):
    print_json(connection.metadata())


def _validate(args, connection):
    payload = None
    if args.xml:
        payload = xml.xml2json(args.xml)
    if args.json:
        payload = json.load(args.json)
    if payload is None:
        print("Please provide an XML or JSON file.")
        return
    resource_bundle = bundle.Bundle('validation', connection.integration)
    resource_bundle.add_payload(payload)
    for model in resource_bundle.unpack():
        print_model(model)


def _activities(args, connection):
    for activity in connection.activities():
        print_model(activity)


def _messages(args, connection):
    for message in connection.search(
            event=args.event,
            status=args.status,
            patient=DummyResource(args.patient),
            batch_size=args.batch_size,
            batch_count=args.batch_count):
        if args.save_in_dir:
            download(connection, args.save_in_dir, msg=message)
        else:
            print_model(message)


def _message(args, connection):
    if args.save_in_dir:
        download(connection, args.save_in_dir, msgid=args.message_id)
    else:
        for model in connection.search(message_id=args.message_id):
            print_model(model)


def _updates(args, connection):
    until = None
    if args.until is not None:
        until = dateutil.parser.parse(args.until, tzinfos=utils.UTC)
    for index, update in enumerate(connection.updates()):
        with update:
            if until is None:
                if not args.all_updates and index:
                    update.postpone()
                    break
            else:
                if update.message.timestamp > until:
                    update.postpone()
                    break
            print_model(update.data)
            if args.failure:
                update.fail(args.failure)


def _launch(args, connection):
    print(
        connection.launch_from_parameters(
            args.application_id,
            args.patient_link,
            args.user_link,
            args.activity,
            ))


def console():
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
    messages.add_argument(
        '--batch-size',
        type=int,
        help='Number of message per bundle.')
    messages.add_argument(
        '--batch-count',
        type=int,
        help='Number of bundles.')
    messages.add_argument(
        '--save-in-dir', type=directory,
        help='Save the source for each messsage listed in the query in '
             'the given directory')

    message = subparsers.add_parser('message')
    message.add_argument(
        'message_id',
        help='internal MessageHeader id or MessageHeader URL.')
    message.add_argument(
        '--save-in-dir', type=directory,
        help='Save the source for the messsage in the given directory')

    updates = subparsers.add_parser('updates')
    updates.add_argument(
        '--all', dest='all_updates', action='store_true',
        help='Process all next messages')
    updates.add_argument(
        '--until',
        help='Process all next messages until the given date (and time)')
    updates.add_argument(
        '--failure',
        help='Fail and set the exception on the messages.')

    launch = subparsers.add_parser('launch')
    launch.add_argument('user_link')
    launch.add_argument('application_id')
    launch.add_argument('patient_link')
    launch.add_argument('--activity', help='activity_identifier')

    args = parser.parse_args()

    root = logging.getLogger()
    root.addHandler(logging.StreamHandler(sys.stdout))

    if args.verbose:
        root.setLevel(logging.DEBUG)
        logger.set_log_level(logging.DEBUG)
    else:
        root.setLevel(logging.ERROR)
        logger.set_log_level(logging.ERROR)

    credentials = get_credentials(args)
    integration = connector.Integration(name='Python command line')
    connection = connector.Connector(credentials, integration)
    commands = {
        'activities': _activities,
        'launch': _launch,
        'message': _message,
        'messages': _messages,
        'metadata': _metadata,
        'updates': _updates,
        'validate': _validate}
    command = commands.get(args.command)
    if command is None:
        sys.exit('Unknown command {}'.format(args.command))
    try:
        command(args, connection)
    except Exception as error:
        if args.post_mortem:
            print(error)
            pdb.post_mortem()
        raise
