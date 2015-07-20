def send_create_or_update_careplan_to_server(
        connector, patient, practitioner, careplan):
    from koppeltaal.activity_definition import parse
    from koppeltaal.create_or_update_care_plan import generate

    # A random activity, could be anything.
    first_activity = list(parse(connector.activity_definition()))[0]
    xml = generate(
        connector.domain, first_activity, patient, careplan, practitioner)
    result = connector.create_or_update_care_plan(xml)
