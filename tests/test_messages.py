def test_messages(connector, patient, practitioner, careplan, activity):
    """Get messages from the server."""
    from koppeltaal.feed import parse
    from koppeltaal.create_or_update_care_plan import generate

    # As nothing was created on the Koppeltaal server for this unique
    # patient, we can trust there're no messages just yet.
    headers = list(parse(connector.messages(patient=patient)))
    assert len(headers) == 0

    # For the given careplan, we post the CreateOrUpdate and thus we should
    # now have a message to retrieve.
    xml = generate(
        connector.domain, activity, careplan, practitioner)
    connector.post_message(xml)
    headers2 = list(parse(connector.messages(patient=patient)))
    assert len(headers2) == 1


def test_messages_for_patient(
        connector, patient, careplan, careplan_on_server):
    """Get messages for a specific patient."""
    from koppeltaal.feed import parse

    # We can trust our patient objects are unique and thus we can trust we
    # have one message here.
    headers = parse(connector.messages(patient=careplan.patient))
    assert len(list(headers)) == 1


def test_messages_for_status(connector, patient, careplan, careplan_on_server):
    """Get messages for a specific status."""
    import koppeltaal.interfaces
    from koppeltaal.feed import parse

    headers = list(parse(connector.messages(patient=careplan.patient)))
    assert len(headers) == 1

    header1 = headers[0]
    assert header1.status == koppeltaal.interfaces.PROCESSING_STATUS_NEW

    headers2 = list(parse(
        connector.messages(
            patient=careplan.patient,
            processing_status=koppeltaal.interfaces.PROCESSING_STATUS_NEW)))
    assert len(headers2) == 1

    # We're talking about the same header here. Checking the versions is
    # kinda circumstantial though. XXX needs something better.
    header2 = headers2[0]
    assert header1.__version__ == header2.__version__

    headers3 = list(parse(
        connector.messages(
            patient=careplan.patient,
            processing_status=koppeltaal.interfaces.PROCESSING_STATUS_CLAIMED))
        )
    assert len(headers3) == 0


def test_message_for_version(connector, careplan_on_server):
    """Get message for a specific version."""
    import koppeltaal
    import koppeltaal.interfaces
    from koppeltaal.feed import parse

    headers = list(parse(
        connector.messages(patient=careplan_on_server.patient, summary=True)))
    version = headers[0].__version__
    message = connector.message(version)
    assert version in message
    assert koppeltaal.url(careplan_on_server) in message


def test_claim(connector, patient, practitioner, careplan, careplan_on_server):
    """Claim a specific message."""
    import koppeltaal.interfaces
    from koppeltaal.feed import parse

    # Get the messages for this patient.
    headers = list(parse(connector.messages(patient=patient)))
    assert len(headers) == 1

    header1 = headers[0]
    assert header1.__version__ is not None
    assert header1.status == koppeltaal.interfaces.PROCESSING_STATUS_NEW

    # Get full message XML.
    full_message = connector.message(header1.__version__)
    assert patient.name.given in full_message

    # Now claim the message.
    connector.claim(header1.__version__)

    # The status is "Claimed".
    headers2 = list(parse(connector.messages(patient=patient)))
    assert len(headers2) == 1

    header2 = headers2[0]
    assert header2.__version__ is not None
    assert header2.__version__ > header1.__version__
    assert header2.status == koppeltaal.interfaces.PROCESSING_STATUS_CLAIMED


def test_success(
        connector, patient, practitioner, careplan, careplan_on_server):
    """Claim a specific message and mark it as a success."""
    import koppeltaal.interfaces
    from koppeltaal.feed import parse

    # Get the messages for this patient.
    headers = list(parse(connector.messages(patient=patient)))
    assert len(headers) == 1

    # Now claim the message and now we have not "new" messages left.
    header = headers[0]
    connector.claim(header.__version__)
    connector.success(header.__version__)
    headers2 = list(parse(
        connector.messages(
            patient=patient,
            processing_status=koppeltaal.interfaces.PROCESSING_STATUS_NEW)))
    assert len(headers2) == 0

    # XXX test retrieve for status Success.
    # XXX We could parse this instead of doing a string check.
    xml = connector.message(header.__version__)
    assert '<valueCode value="{}" />'.format(
        koppeltaal.interfaces.PROCESSING_STATUS_SUCCESS) in xml


def test_cannot_finalize_non_claimed_message(connector):
    """When we try to finalize a message that we hadn't claimed before, this
    should yield an error.

    """
