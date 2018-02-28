# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 - 2017 Stichting Koppeltaal
:license: AGPL, see `LICENSE.md` for more details.
"""

from koppeltaal import (interfaces, logger)


def extensions(extensions, namespace=interfaces.NAMESPACE):
    """Update extensions from an older version of Koppeltaal to the
    currently supported one.
    """
    subactivities = extensions.get(namespace + 'CarePlan#SubActivity', [])
    for subactivity in subactivities:
        if 'valueString' in subactivity:
            logger.warning('Detected 1.0 subactivity in care plan.')
            subactivity['extension'] = [{
                'url': namespace + 'CarePlan#SubActivityIdentifier',
                'valueString': subactivity['valueString']}
            ]
            del subactivity['valueString']
