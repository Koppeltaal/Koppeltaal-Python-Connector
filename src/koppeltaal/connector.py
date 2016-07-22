import zope.interface

from koppeltaal.fhir import bundle, resource
from koppeltaal import(
    interfaces,
    logger,
    models,
    transport,
    utils)

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

    def __init__(self, message, ack_function):
        self.message = message
        self.data = message.data
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
            self.message.status = models.Status()
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

    def __init__(self, server, username, password, domain, integration):
        self.transport = self._create_transport(server, username, password)
        self.domain = domain
        self.integration = integration

    def _fetch_bundle(self, url, params=None):
        next_url = url
        next_params = params
        packaging = bundle.Bundle(self.domain, self.integration)
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
            activity_identifier):
        assert application_id is not None, 'Invalid activity'
        assert patient_link is not None, 'Invalid patient'
        assert user_link is not None, 'Invalid user'
        params = {
            'client_id': application_id,
            'patient': patient_link,
            'user': user_link,
            'resource': activity_identifier}
        return self.transport.query_redirect(
            interfaces.OAUTH_LAUNCH_URL, params)

    def updates(self):

        def send_back(message):
            packaging = resource.Resource(self.domain, self.integration)
            packaging.add_model(message)
            self.transport.update(message.fhir_link, packaging.get_payload())

        def send_back_on_transaction(message):
            return self.integration.transaction_hook(send_back, message)

        p = {'_query': 'MessageHeader.GetNextNewAndClaim'}
        while True:
            try:
                bundle = self._fetch_bundle(interfaces.MESSAGE_HEADER_URL, p)
                message = bundle.unpack_message_header()
            except interfaces.InvalidBundle as error:
                logger.error(
                    'Bundle error while reading message: {}'.format(error))
                continue
            except interfaces.InvalidResponse as error:
                logger.error(
                    'Transport error while reading mailbox: {}'.format(error))
                break

            if message is None:
                # We are out of messages
                break
            update = Update(message, send_back_on_transaction)
            errors = bundle.errors()
            if errors:
                logger.error('Error while reading message: {}'.format(errors))
                with update:
                    update.fail(u', '.join([u"Resource '{}': {}".format(
                        e.fhir_link, e.error) for e in errors]))
            else:
                yield update

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
        identifier = utils.messageid()
        source = models.MessageHeaderSource(
            name=unicode(self.integration.name),
            endpoint=unicode(self.integration.url),
            software=unicode(interfaces.SOFTWARE),
            version=unicode(interfaces.VERSION))
        message = models.MessageHeader(
            timestamp=utils.now(),
            event=event,
            identifier=identifier,
            data=data,
            source=source,
            patient=patient)
        send_bundle = bundle.Bundle(self.domain, self.integration)
        send_bundle.add_model(message)
        response_bundle = bundle.Bundle(self.domain, self.integration)
        response_bundle.add_payload(
            self.transport.create(
                interfaces.MAILBOX_URL,
                send_bundle.get_payload()))
        response = response_bundle.unpack_message_header()
        if (response is None or
                response.response is None or
                response.response.identifier != identifier or
                response.response.code != "ok"):
            raise interfaces.InvalidResponse(response)
        return response.data
