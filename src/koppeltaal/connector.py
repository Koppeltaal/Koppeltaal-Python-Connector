import uuid
import zope.interface

from koppeltaal.fhir import bundle
from koppeltaal import(
    interfaces,
    models,
    transport,
    utils)

DEFAULT_COUNT = 100


class FHIRLinkGenerator(object):

    def __init__(self, endpoint='https://example.com/fhir/Koppeltaal'):
        self.endpoint = endpoint

    def model_id(self, model):
        # You should in your implementation extend this class and
        # re-implement this method so that model_id() of a given model
        # always return the exact same id. This is NOT done here in
        # this simplistic default implementation.
        return id(model)

    def __call__(self, model, resource_type):
        return '{}/{}/{}'.format(
            self.base_url, resource_type, self.model_id(model))


@zope.interface.implementer(interfaces.IConnector)
class Connector(object):

    def __init__(self, server, username, password, domain, link_generator):
        self.transport = transport.Transport(server, username, password)
        self.domain = domain
        self.link_generator = link_generator

    def _fetch_bundle(self, url, params=None):
        next_url = url
        next_params = params
        resource_bundle = bundle.Bundle(self.domain, self.link_generator)
        while next_url:
            response = self.transport.query(next_url, next_params)
            resource_bundle.add_payload(response)
            next_url = utils.json2links(response).get('next')
            next_params = None  # Parameters are already in the next link.
        return resource_bundle.unpack()

    def metadata(self):
        return self.transport.query(interfaces.METADATA_URL)

    def activities(self):
        return self._fetch_bundle(
            interfaces.ACTIVITY_DEFINITION_URL, {'code': 'ActivityDefinition'})

    def activity(self, identifier):
        for activity in self.activities():
            if activity.identifier == identifier:
                return activity
        return None

    def launch(self, activity, patient, user):
        params = {
            'client_id': activity.identifier,
            'patient': patient.fhir_link,
            'user': user.fhir_link,
            'resource': activity.identifier}
        return self.transport.query_redirect(
            interfaces.OAUTH_LAUNCH_URL, params)

    def fetch(
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
        return self._fetch_bundle(interfaces.MESSAGE_HEADER_URL, params)

    def send(self, event, data, patient):
        source = models.Source(
            endpoint=unicode(self.link_generator.endpoint),
            software=unicode(interfaces.SOFTWARE),
            version=unicode(interfaces.VERSION))
        message = models.MessageHeader(
            timestamp=utils.now(),
            event=event,
            identifier=unicode(uuid.uuid4()),
            data=data,
            source=source,
            patient=patient)
        resource_bundle = bundle.Bundle(self.domain, self.link_generator)
        resource_bundle.add_model(message)
        return resource_bundle.get_payload()
