import feedreader.parser
import koppeltaal


def parse(xml):
    """
    Pass in a raw activity definition, will generate a list of activity
    information.

    In the future, we may accept filtering criteria here, such as the
    ActivityKind, in order to only accept a certain kind of Activities.
    """
    feed = feedreader.parser.from_string(xml)
    for entry in feed.entries:
        node = entry._xml.content.find(
            'fhir:Other', namespaces=koppeltaal.NS)
        # Make 'useful' attributes accessible here.
        activity_kind_value_coding = node.find(
            'fhir:extension[@url="{koppeltaal}/ActivityDefinition#ActivityKind"]'.format(
                **koppeltaal.NS), namespaces=koppeltaal.NS).find(
            'fhir:valueCoding', namespaces=koppeltaal.NS)
        yield {
            'node': node,
            # The raw element. We may want to remove this at some point in the
            # future.
            'identifier': node.find(
                'fhir:identifier', namespaces=koppeltaal.NS).find(
                    'fhir:value', namespaces=koppeltaal.NS).get('value'),
            'ActivityName': node.find(
                'fhir:extension[@url="{koppeltaal}/ActivityDefinition#ActivityName"]'.format(
                    **koppeltaal.NS), namespaces=koppeltaal.NS).find(
                    'fhir:valueString', namespaces=koppeltaal.NS).get('value'),
            'ActivityKind': {
                'code': activity_kind_value_coding.find('fhir:code',
                    namespaces=koppeltaal.NS).get('value'),
                'display': activity_kind_value_coding.find('fhir:display',
                    namespaces=koppeltaal.NS).get('value')
            }
        }


def activity_info(xml, activity_id):
    '''Given an XML feed of Activities, return the info about the one with the
    given activity_id.'''
    for info in parse(xml):
        if info['identifier'] == activity_id:
            return info
    # Raise an error in case of unknown activity id.
    raise koppeltaal.KoppeltaalException(
        'Unknown activity id: "{}"'.format(activity_id))
