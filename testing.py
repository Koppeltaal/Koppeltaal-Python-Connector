def send_create_or_update_careplan_to_server(
        connector, patient, practitioner, careplan):
    from koppeltaal.activity_definition import parse
    from koppeltaal.message import parse_feed, parse_messages
    from koppeltaal.create_or_update_care_plan import generate
    # A random activity, could be anything.
    first_activity = list(parse(connector.activity_definition()))[0]

    xml = generate(
        connector.domain, first_activity, patient, careplan, practitioner)
    result = connector.create_or_update_care_plan(xml)

    # The careplan was sent successfully and now has a _history.
    result = parse_feed(result)
    assert careplan.url in result['reference']

    # Assert there is a message in the mailbox for this patient.
    messages_for_pat = parse_messages(connector.messages(
        patient_url=patient.url))
    assert len(messages_for_pat.entries) == 1
