# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import six
import zope.interface

from koppeltaal.fhir import bundle, resource
from koppeltaal import (
    interfaces,
    definitions,
    logger,
    models,
    transport,
    utils)
from six.moves.urllib.parse import urlencode


unicode = six.text_type


DEFAULT_COUNT = 100


@zope.interface.implementer(interfaces.IIntegration)
class Integration(object):

    def __init__(
            self,
            name='Generic python application',
            url='https://example.com/fhir/Koppeltaal'):
        self.name = name
        self.url = url

    def transaction_hook(self, commit_function, message):
        return commit_function(message)

    def model_id(self, model):
        # You should in your implementation extend this class and
        # re-implement this method so that model_id() of a given model
        # always return the exact same id. This is NOT done here in
        # this simplistic default implementation.
        return id(model)

    def fhir_link(self, model, resource_type):
        return '{}/{}/{}'.format(
            self.url, resource_type, self.model_id(model))


@zope.interface.implementer(interfaces.IUpdate)
class Update(object):

    def __init__(self, message, resources, ack_function):
        self.message = message
        self.resources = resources
        assert len(message.data) == 1, 'Multiple focal resources found'
        self.data = message.data[0]
        self.patient = message.patient
        self._ack_function = ack_function

    def __enter__(self):
        self.acked = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and exc_val is None and exc_tb is None:
            if self.acked is False:
                self.success()
        else:
            # There was an exception. We put back the message to new
            # since we assume we can be solved after.
            self.ack('New')
        if self.acked is not None:
            self._ack_function(self.message)

    def ack(self, status, exception=None):
        self.acked = True
        if self.message.status is None:
            self.message.status = models.ProcessingStatus()
        self.message.status.status = status
        self.message.status.exception = exception
        self.message.status.last_changed = utils.now()

    def success(self):
        self.ack('Success')

    def fail(self, exception="FAILED"):
        self.ack('Failed', unicode(exception))

    def postpone(self):
        self.acked = None


@zope.interface.implementer(interfaces.IConnector)
class Connector(object):
    _create_transport = transport.Transport

    def __init__(self, credentials, integration):
        self._credentials = credentials
        self.transport = self._create_transport(
            self._credentials.url,
            self._credentials.username,
            self._credentials.password)
        self.domain = self._credentials.domain
        self.integration = integration

    def _fetch_bundle(self, url, params=None, batch_count=None):
        count = 0
        next_url = url
        next_params = params
        packaging = bundle.Bundle(self.domain, self.integration)
        while next_url:
            response = self.transport.query(next_url, next_params)
            packaging.add_payload(response.json)
            next_url = utils.json2links(response.json).get('next')
            next_params = None  # Parameters are already in the next link.
            count += 1
            if batch_count is not None and count >= batch_count:
                break
        return packaging

    def metadata(self):
        return self.transport.query(interfaces.METADATA_URL).json

    def activities(self, archived=False):
        params = {'code': 'ActivityDefinition'}
        if archived:
            params['includearchived'] = 'yes'
        return self._fetch_bundle(
            interfaces.ACTIVITY_DEFINITION_URL, params).unpack()

    def activity(self, identifier, archived=False):
        for activity in self.activities(archived=archived):
            if activity.identifier == identifier:
                return activity
        return None

    def send_activity(self, activity):
        packaging = resource.Resource(self.domain, self.integration)
        packaging.add_model(activity)
        payload = packaging.get_payload()
        if activity.fhir_link is not None:
            response = self.transport.update(activity.fhir_link, payload)
        else:
            response = self.transport.create(interfaces.OTHER_URL, payload)
        if response.location is None:
            raise interfaces.ResponseError(response)
        activity.fhir_link = response.location
        return activity

    def launch(self, careplan, user=None, activity_identifier=None):
        activity = None
        for candidate in careplan.activities:
            if (activity_identifier is None or
                    candidate.identifier == activity_identifier):
                activity = candidate
                break
        if activity is None:
            raise interfaces.KoppeltaalError('No activity found')
        if user is None:
            user = careplan.patient
        application_id = None
        if activity.definition is not None:
            activity_definition = self.activity(activity.definition)
            assert interfaces.IReferredFHIRResource.providedBy(
                activity_definition.application)
            application_id = activity_definition.application.display
        return self.launch_from_parameters(
            application_id,
            careplan.patient.fhir_link,
            user.fhir_link,
            activity.identifier)

    def launch_from_parameters(
            self,
            application_id,
            patient_link,
            user_link,
            activity_identifier,
            intent=None):
        assert application_id is not None, 'Invalid activity'
        assert patient_link is not None, 'Invalid patient'
        assert user_link is not None, 'Invalid user'
        params = {
            'client_id': application_id,
            'patient': patient_link,
            'user': user_link,
            'resource': activity_identifier}
        if intent is not None:
            params['intent'] = intent
        return self.transport.query_redirect(
            interfaces.OAUTH_LAUNCH_URL, params).location

    def authorize_from_parameters(
            self,
            application_id,
            launch_id,
            redirect_uri):
        assert application_id is not None, 'Invalid activity'
        return '{}?{}'.format(
            self.transport.absolute_url(interfaces.OAUTH_AUTHORIZE_URL),
            urlencode(
                (('client_id', application_id),
                 ('redirect_uri', redirect_uri),
                 ('response_type', 'code'),
                 ('scope', 'patient/*.read launch:{}'.format(launch_id)))))

    def token_from_parameters(self, code, redirect_url):
        params = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_url}
        # Note how for this specific request a different set of credentials
        # ought to be used.
        # See https://www.koppeltaal.nl/
        #    wiki/Technical_Design_Document_Koppeltaal_1.1.1
        #    #6._Game_retrieves_an_Access_token
        username = self.integration.client_id
        password = self.integration.client_secret
        assert username is not None, 'client id missing'
        assert password is not None, 'client secret missing'
        return self.transport.query(
            interfaces.OAUTH_TOKEN_URL,
            params=params,
            username=username,
            password=password).json

    def updates(
        self,
        expected_events=None,
        patient=None,
        event=None):

        def send_back(message):
            packaging = resource.Resource(self.domain, self.integration)
            packaging.add_model(message)
            self.transport.update(message.fhir_link, packaging.get_payload())

        def send_back_on_transaction(message):
            return self.integration.transaction_hook(send_back, message)

        parameters = {'_query': 'MessageHeader.GetNextNewAndClaim'}
        if patient is not None:
            parameters['Patient'] = patient
        if event is not None:
            parameters['event'] = event

        while True:
            try:
                bundle = self._fetch_bundle(
                    interfaces.MESSAGE_HEADER_URL, parameters)
                message = bundle.unpack_model(definitions.MessageHeader)
            except interfaces.InvalidBundle as error:
                logger.error(
                    'Bundle error while reading message: {}'.format(error))
                continue
            except interfaces.TransportError as error:
                logger.error(
                    'Transport error while reading mailbox: {}'.format(error))
                break

            if message is None:
                # We are out of messages
                break

            update = Update(message, bundle.unpack, send_back_on_transaction)
            errors = bundle.errors()
            if errors:
                reason = u', '.join([str(error) for error in errors])
                logger.error(
                    "Error while reading message '{}': {}".format(
                        message.fhir_link, reason))
                with update:
                    update.fail(reason)
            elif (expected_events is not None
                  and message.event not in expected_events):
                logger.warning(
                    "Event '{}' not expected in message '{}'".format(
                        message.event, message.fhir_link))
                with update:
                    update.fail('Event not expected')
            elif (message.source is not None and
                  message.source.endpoint == self.integration.url):
                logger.info(
                    'Event "{}" originated from our endpoint '
                    '"{}"'.format(message.event, self.integration.url))
                with update:
                    # We are the sender ourselves. Ack those messages.
                    update.success()
            else:
                yield update

    def search(
            self, message_id=None, event=None, status=None, patient=None,
            batch_size=DEFAULT_COUNT, batch_count=None):
        params = {}
        if message_id:
            params['_id'] = message_id
        else:
            params['_summary'] = 'true'
            params['_count'] = batch_size
        if event:
            params['event'] = event
        if status:
            params['ProcessingStatus'] = status
        if patient:
            params['Patient'] = patient.fhir_link
        return self._fetch_bundle(
            interfaces.MESSAGE_HEADER_URL, params, batch_count).unpack()

    def send(self, event, data, patient=None):
        identifier = utils.messageid()
        source = models.MessageHeaderSource(
            name=unicode(self.integration.name),
            endpoint=unicode(self.integration.url),
            software=unicode(interfaces.SOFTWARE),
            version=unicode(interfaces.VERSION))
        request_message = models.MessageHeader(
            timestamp=utils.now(),
            event=event,
            identifier=identifier,
            data=[data],
            source=source,
            patient=patient)
        request_bundle = bundle.Bundle(self.domain, self.integration)
        request_bundle.add_model(request_message)
        request_payload = request_bundle.get_payload()

        try:
            response = self.transport.create(
                interfaces.MAILBOX_URL, request_payload)
        except interfaces.ResponseError as error:
            response_resource = resource.Resource(
                self.domain, self.integration)
            response_resource.add_payload(error.response.json)
            outcome = response_resource.unpack_model(
                definitions.OperationOutcome)
            raise interfaces.OperationOutcomeError(outcome)

        response_bundle = bundle.Bundle(self.domain, self.integration)
        response_bundle.add_payload(response.json)
        response_message = response_bundle.unpack_model(
            definitions.MessageHeader)
        if (response_message is None or
                response_message.event != event or
                response_message.response is None or
                response_message.response.identifier != identifier or
                response_message.response.code != "ok"):
            raise interfaces.MessageResponseError(response_message)
        return response_message.data

    def close(self):
        self.transport.close()


@zope.interface.implementer(interfaces.IConnector)
class DummyConnector(object):
    """A dummy connector follows the API of a connector but do not do
    anything.
    """
    _create_transport = None

    def __init__(self, credentials, integration):
        self.transport = None
        self.domain = credentials.domain
        self.integration = integration

    def metadata(self):
        return {
            'name': 'Koppeltaal',
            'version': 'v1.1',
            'fhirVersion': '0.0.82'}

    def activities(self, archived=False):
        return []

    def activity(self, identifier, archived=False):
        return None

    def send_activity(self, activity):
        raise interfaces.DummyError()

    def launch(self, careplan, user=None, activity_identifier=None):
        raise interfaces.DummyError()

    def launch_from_parameters(
            self,
            application_id,
            patient_link,
            user_link,
            activity_identifier):
        raise interfaces.DummyError()

    def authorize_from_parameters(
            self,
            application_id,
            launch_id,
            redirect_uri):
        raise interfaces.DummyError()

    def token_from_parameters(self, code, redirect_url):
        return {}

    def updates(self, expected_events=None):
        return []

    def search(
            self, message_id=None, event=None, status=None, patient=None):
        return None

    def send(self, event, data, patient=None):
        raise interfaces.DummyError()

    def close(self):
        pass
