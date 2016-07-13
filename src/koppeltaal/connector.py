import contextlib
import uuid
import zope.interface

from koppeltaal.fhir import bundle, resource
from koppeltaal import(
    interfaces,
    models,
    transport,
    utils)

DEFAULT_COUNT = 100


@zope.interface.implementer(interfaces.IFHIRConfiguration)
class FHIRConfiguration(object):

    def __init__(
            self,
            name='Generic python application',
            url='https://example.com/fhir/Koppeltaal'):
        self.name = name
        self.url = url

    def model_id(self, model):
        # You should in your implementation extend this class and
        # re-implement this method so that model_id() of a given model
        # always return the exact same id. This is NOT done here in
        # this simplistic default implementation.
        return id(model)

    def link(self, model, resource_type):
        return '{}/{}/{}'.format(
            self.url, resource_type, self.model_id(model))


class Update(object):

    def __init__(self, message, finalize):
        self.message = message
        self.data = message.data
        self._finalize = finalize

    def __enter__(self):
        self.updated = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and exc_val is None and exc_tb is None:
            self.success()
        else:
            # There was an exception. We put back the message to new
            # since we assume we can be solved after.
            self.mark('New')
        if self.updated is not None:
            self._finalize(self.message)

    def mark(self, status, exception=None):
        if self.updated is not False:
            return
        self.updated = True
        if self.message.status is None:
            self.message.status = models.Status()
        self.message.status.status = status
        self.message.status.exception = exception
        self.message.status.last_changed = utils.now()

    def success(self):
        self.mark('Success')

    def fail(self, exception="FAILED"):
        self.mark('Failed', unicode(exception))

    def postpone(self):
        self.updated = None


@zope.interface.implementer(interfaces.IConnector)
class Connector(object):

    def __init__(self, server, username, password, domain, configuration):
        self.transport = transport.Transport(server, username, password)
        self.domain = domain
        self.configuration = configuration

    def _fetch_bundle(self, url, params=None):
        next_url = url
        next_params = params
        packaging = bundle.Bundle(self.domain, self.configuration)
        while next_url:
            response = self.transport.query(next_url, next_params)
            packaging.add_payload(response)
            next_url = utils.json2links(response).get('next')
            next_params = None  # Parameters are already in the next link.
        return packaging

    def metadata(self):
        return self.transport.query(interfaces.METADATA_URL)

    def activities(self):
        return self._fetch_bundle(
            interfaces.ACTIVITY_DEFINITION_URL,
            {'code': 'ActivityDefinition'}).unpack()

    def activity(self, identifier):
        for activity in self.activities():
            if activity.identifier == identifier:
                return activity
        return None

    def launch(self, activity, patient, user, resource=None):
        params = {
            'client_id': activity.identifier,
            'patient': patient.fhir_link,
            'user': user.fhir_link,
            'resource': resource or activity.identifier}
        return self.transport.query_redirect(
            interfaces.OAUTH_LAUNCH_URL, params)

    def updates(self):

        def send_back(message):
            packaging = resource.Resource(self.domain, self.configuration)
            packaging.add_model(message)
            self.transport.update(message.fhir_link, packaging.get_payload())

        params = {'_query': 'MessageHeader.GetNextNewAndClaim'}
        while True:
            message = self._fetch_bundle(
                interfaces.MESSAGE_HEADER_URL, params).unpack_message_header()
            if message is None:
                break
            yield Update(message, send_back)

    def search(
            self, message_id=None, event=None, status=None, patient=None):
        params = {}
        if message_id:
            params['_id'] = message_id
        else:
            params['_summary'] = 'true'
            params['_count'] = DEFAULT_COUNT
        if event:
            params['event'] = event
        if status:
            params['ProcessingStatus'] = status
        if patient:
            params['Patient'] = patient.fhir_link
        return self._fetch_bundle(
            interfaces.MESSAGE_HEADER_URL,
            params).unpack()

    def send(self, event, data, patient):
        identifier = unicode(uuid.uuid4())
        source = models.MessageHeaderSource(
            name=unicode(self.configuration.name),
            endpoint=unicode(self.configuration.url),
            software=unicode(interfaces.SOFTWARE),
            version=unicode(interfaces.VERSION))
        message = models.MessageHeader(
            timestamp=utils.now(),
            event=event,
            identifier=identifier,
            data=data,
            source=source,
            patient=patient)
        send_bundle = bundle.Bundle(self.domain, self.configuration)
        send_bundle.add_model(message)
        response_bundle = bundle.Bundle(self.domain, self.configuration)
        response_bundle.add_payload(
            self.transport.create(
                interfaces.MAILBOX_URL,
                send_bundle.get_payload()))
        response = response_bundle.unpack_message_header()
        assert response.response.identifier == identifier
        if response.response.code != "ok":
            raise interfaces.InvalidResponse(response)
        return response.data
