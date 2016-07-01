import json
import dateutil.parser
import koppeltaal.models
import koppeltaal.utils

NAMESPACE = 'http://ggz.koppeltaal.nl/fhir/Koppeltaal/'
MARKER = object()


class ActivityDefinition(object):

    @classmethod
    def unpack(self, item):
        return koppeltaal.models.Activity(
            item.uid,
            item.extension('ActivityDefinition#ActivityDefinitionIdentifier'),
            item.extension('ActivityDefinition#ActivityKind'),
            item.extension('ActivityDefinition#ActivityName'),
            item.extension('ActivityDefinition#DefaultPerformer'),
            item.extension('ActivityDefinition#IsActive'),
            item.extension('ActivityDefinition#IsDomainSpecific'),
            item.extension('ActivityDefinition#LaunchType'),
            item.extension('ActivityDefinition#IsArchived'))


class MessageHeader(object):

    @classmethod
    def unpack(self, item):
        status = item.extension('MessageHeader#ProcessingStatus')
        return koppeltaal.models.Message(
            item.uid,
            item['event']['code'],
            status('MessageHeader#ProcessingStatusStatus'),
            status('MessageHeader#ProcessingStatusStatusLastChanged'),
            item.extension('MessageHeader#Patient'))


class Patient(object):

    @classmethod
    def unpack(self, item):
        return koppeltaal.models.Patient(
            item.uid,
            item['name'][0]['family'][0],
            item['name'][0]['given'][0])


class Practitioner(object):

    @classmethod
    def unpack(self, item):
        return koppeltaal.models.Practitioner(
            item.uid,
            item['name']['family'][0],
            item['name']['given'][0])


FACTORIES = {
    'ActivityDefinition': ActivityDefinition,
    'MessageHeader': MessageHeader,
    'Patient': Patient,
    'Practitioner': Practitioner
}


class ResourceExtension(object):

    def __init__(self, content, bundle):
        self._bundle = bundle
        self._index = {}
        if 'extension' in content:
            for extension in content['extension']:
                url = extension['url']
                if url.startswith(NAMESPACE):
                    url = extension['url'][len(NAMESPACE):]
                self._index[url] = extension

    def __call__(self, url):
        if url not in self._index:
            return None
        extension = self._index[url]
        for key in ("valueString", "valueBoolean", "valueCode"):
            if key in extension:
                return extension[key]
        if "valueCoding" in extension:
            return extension["valueCoding"]["code"]
        if "valueInstant" in extension:
            return dateutil.parser.parse(extension["valueInstant"])
        if "valueResource" in extension:
            reference = self._bundle.find(extension["valueResource"])
            if reference:
                return reference.unpack()
            return None
        if "extension" in extension:
            return ResourceExtension(extension, self._bundle)
        raise NotImplementedError()


class BundleItem(object):
    unpacked_item = MARKER

    def __init__(self, bundle, entry):
        self.uids = filter(
            None,
            [entry['id'], koppeltaal.utils.json2links(entry).get('self')])
        self.__content = entry['content'].copy()
        resource_type = self.__content.pop('resourceType', 'Other')
        if resource_type == 'Other':
            assert 'code' in self.__content
            for code in self.__content.pop('code').get('coding', []):
                resource_type = code.get('code', 'Other')
        assert resource_type != 'Other'
        self.resource_type = resource_type
        self.extension = ResourceExtension(entry['content'], bundle)

    @property
    def uid(self):
        return self.uids[0]

    def unpack(self):
        if self.unpacked_item is MARKER:
            factory = FACTORIES.get(self.resource_type)
            if factory:
                self.unpacked_item = factory.unpack(self)
            else:
                self.unpacked_item = None
        return self.unpacked_item

    def __getitem__(self, key):
        return self.__content[key]

    def __eq__(self, other):
        if isinstance(other, dict):
            return other.get('reference', None) in self.uids
        return NotImplemented()

    def __format__(self, _):
        return '<BundleItem uids="{}" type="{}">{}</BundleItem>'.format(
            ', '.join(self.uids),
            self.resource_type,
            json.dumps(self.__content, indent=2, sort_keys=True))


class Bundle(object):

    def __init__(self):
        self.items = []

    def add(self, entry):
        item = BundleItem(self, entry)
        print '{}'.format(item)
        self.items.append(item)

    def find(self, reference):
        for item in self.items:
            if reference == item:
                return item
        return None

    def unpack(self):
        for item in self.items:
            yield item.unpack()
