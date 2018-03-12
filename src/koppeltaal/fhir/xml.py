# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

import lxml.etree
import six

from koppeltaal import fhir


unicode = six.text_type


TYPES = [
    (('extension', 'valueInteger'), 'int'),
    (('extension', 'valueDecimal'), 'float'),
    (('extension', 'valueBoolean'), 'boolean'),
    (('activity', 'prohibited'), 'boolean'),
    (('Patient', 'active'), 'boolean'),
]


def type_for(node_tag, child_tag):
    # Replace this by checking the definition.
    for key, value in TYPES:
        if (node_tag, child_tag) == key:
            return value
    return 'string'


def tag(node, namespace="atom"):
    tag = node.tag
    if namespace == "atom":
        namespace = '{http://www.w3.org/2005/Atom}'
    elif namespace == "fhir":
        namespace = '{http://hl7.org/fhir}'
    if tag.startswith(namespace):
        return tag[len(namespace):]
    return tag


def fhir2json(node, repeatable_field_names):
    node_tag = tag(node, "fhir")
    result = dict(node.attrib)
    for child in node.getchildren():
        child_tag = tag(child, "fhir")
        if child_tag == '{http://www.w3.org/1999/xhtml}div':
            child_tag = 'div'
            child_value = lxml.etree.tostring(child)
        elif len(child.getchildren()):
            child_value = fhir2json(child, repeatable_field_names)
            child_value.update(child.attrib)
        else:
            assert 'value' in child.attrib
            child_value_type = type_for(node_tag, child_tag)
            if child_value_type == 'int':
                child_value = int(child.attrib['value'])
            elif child_value_type == 'float':
                child_value = float(child.attrib['value'])
            elif child_value_type == 'boolean':
                child_value = child.attrib['value'] == 'true'
            else:
                child_value = unicode(child.attrib['value'])
        if child_tag in repeatable_field_names:
            result.setdefault(child_tag, []).append(child_value)
        else:
            assert child_tag not in result, \
                'Invalid fhir file: {} already present.'.format(child_tag)
            result[child_tag] = child_value
    return result


def atom2json(node, is_entry=False):
    result = {}
    for child in node.getchildren():
        child_tag = tag(child, "atom")
        if child_tag in {'id', 'updated', 'title'}:
            result[child_tag] = child.text
        if child_tag in {'category', 'link'}:
            child_value = result.setdefault(child_tag, [])
            child_value.append(dict(child.attrib))
        if child_tag == 'entry':
            assert not is_entry, 'Invalid atom file'
            child_value = result.setdefault(child_tag, [])
            child_value.append(atom2json(child, is_entry=True))
        if child_tag == 'content':
            assert is_entry, 'Invalid atom file'
            assert len(child.getchildren()), 'Invalid fhir file'
            fhir_node = child.getchildren()[0]
            fhir_type = tag(fhir_node, "fhir")
            field_names = fhir.REGISTRY.repeatable_field_names(fhir_type)
            child_value = {'resourceType': fhir_type}
            child_value.update(fhir2json(fhir_node, field_names))
            result[child_tag] = child_value
    return result


def xml2json(xml_file):
    feed = lxml.etree.parse(xml_file).getroot()
    assert tag(feed, "atom") == 'feed', 'Invalid atom file'

    bundle = {'resourceType': 'Bundle'}
    bundle.update(atom2json(feed))
    return bundle
