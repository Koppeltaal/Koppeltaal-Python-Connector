def test_extract(other_node):
    from koppeltaal.interfaces import NS
    from koppeltaal.message import Other
    from koppeltaal.message import extract

    other = Other.from_entry(other_node)
    e1, e2, e3 = other.__node__.xpath('./fhir:extension', namespaces=NS)[:3]

    assert extract(e1) == (
        'https://app.minddistrict.com/c/d78827453a734023853d294e6d3385aa'
        '/remoteactivities/r.1')
    assert extract(e2) == 0
    assert extract(e3) == (
        'http://ggz.koppeltaal.nl/fhir/Koppeltaal/CarePlanActivityStatus',
        'InProgress',
        'InProgress')


def test_get_new_messageheaders(
        connector, patient, activity, careplan, practitioner):

    import koppeltaal
    import koppeltaal.message
    import koppeltaal.create_or_update_care_plan

    # As nothing was created on the Koppeltaal server for this unique
    # patient, we can trust there're no messages just yet.
    headers = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient))
    assert len(headers) == 0

    # Create a careplan, just to have a messageheader available.
    # XXX replace API.
    xml = koppeltaal.create_or_update_care_plan.generate(
        connector.domain, activity, careplan, practitioner)
    koppeltaal.create_or_update_care_plan.parse_result(
        connector.post_message(xml), careplan)  # updates version.

    headers2 = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient))
    assert len(headers2) == 1

    header = headers2[0]
    assert header.patient() == koppeltaal.url(patient)
    assert header.focal_resource() == koppeltaal.url(careplan)
    assert header.status() == koppeltaal.interfaces.STATUS_NEW


def test_get_new_messageheaders_batched(
        connector, patient, activity, practitioner):

    import koppeltaal
    import koppeltaal.model
    import koppeltaal.message
    import koppeltaal.create_or_update_care_plan

    # As nothing was created on the Koppeltaal server for this unique
    # patient, we can trust there're no messages just yet.
    headers = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient))
    assert len(headers) == 0

    # Create a few careplans, just to have messageheaders available.
    # XXX replace API.
    cp1 = koppeltaal.model.CarePlan(patient)
    cp2 = koppeltaal.model.CarePlan(patient)
    cp3 = koppeltaal.model.CarePlan(patient)
    cp4 = koppeltaal.model.CarePlan(patient)
    for cp in [cp1, cp2, cp3, cp4]:
        xml = koppeltaal.create_or_update_care_plan.generate(
            connector.domain, activity, cp, practitioner)
        koppeltaal.create_or_update_care_plan.parse_result(
            connector.post_message(xml), cp)

    headers2 = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient, _batchsize=1))
    assert len(headers2) == 4
    assert [h.patient() for h in headers2] == [koppeltaal.url(patient)] * 4
    assert [h.focal_resource() for h in headers2] == \
        map(koppeltaal.url, [cp1, cp2, cp3, cp4])
    assert [h.status() for h in headers2] == \
        [koppeltaal.interfaces.STATUS_NEW] * 4


def test_get_message(
        connector, patient, activity, careplan, practitioner):

    import koppeltaal
    import koppeltaal.message
    import koppeltaal.create_or_update_care_plan

    # Create a careplan, just to have a messageheader available.
    # XXX replace API.
    xml = koppeltaal.create_or_update_care_plan.generate(
        connector.domain, activity, careplan, practitioner)
    koppeltaal.create_or_update_care_plan.parse_result(
        connector.post_message(xml), careplan)  # updates version.

    headers = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient))
    header = headers[0]
    message = koppeltaal.message.get_message(connector, header)
    assert message.messageheader().__version__ == header.__version__
    # assert message.careplan() == koppeltaal.url(careplan)


def test_claim_message(
        connector, patient, activity, careplan, practitioner):

    import koppeltaal
    import koppeltaal.message
    import koppeltaal.create_or_update_care_plan

    # Create a careplan, just to have a messageheader available.
    # XXX replace API.
    xml = koppeltaal.create_or_update_care_plan.generate(
        connector.domain, activity, careplan, practitioner)
    koppeltaal.create_or_update_care_plan.parse_result(
        connector.post_message(xml), careplan)  # updates version.

    # Unclaimed message
    headers = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient))
    header = headers[0]
    message = koppeltaal.message.get_message(connector, header)
    assert message.messageheader().__version__ == header.__version__
    assert header.status() == koppeltaal.interfaces.STATUS_NEW

    claimed = koppeltaal.message.claim_message(connector, header)
    headers2 = list(
        koppeltaal.message.get_new_messageheaders(
            connector, patient=patient))
    assert len(headers2) == 0
    assert claimed.messageheader().status() == \
        koppeltaal.interfaces.STATUS_CLAIMED

    successed = koppeltaal.message.success_message(connector, header)
    assert successed.messageheader().status() == \
        koppeltaal.interfaces.STATUS_SUCCESS
