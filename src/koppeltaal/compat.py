
from koppeltaal import (interfaces, logger)


def extensions(extensions, namespace=interfaces.NAMESPACE):
    """Update extensions from an older version of Koppeltaal to the
    currently supported one.
    """
    subactivities = extensions.get(namespace + 'CarePlan#SubActivity', [])
    for subactivity in subactivities:
        if 'valueString' in subactivity:
            logger.warn('Detected 1.0 subactivity in care plan.')
            subactivity['extension'] = [{
                'url': namespace + 'CarePlan#SubActivityIdentifier',
                'valueString': subactivity['valueString']}
            ]
            del subactivity['valueString']