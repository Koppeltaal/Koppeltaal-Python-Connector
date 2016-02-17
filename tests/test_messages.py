import pytest

def test_messages(connector, patient, practitioner, careplan, activity):
    '''Get messages from the server.'''
    from koppeltaal.feed import parse
    from koppeltaal.create_or_update_care_plan import generate

    def get_num_messages(patient_url):
        return len(list(parse(connector.messages(
            summary=True,
            patient_url=patient_url))))

    # We use the careplan fixture so we know there's at least one message in
    # the mailbox.
    num_messages_before = get_num_messages(careplan.patient.url)
    xml = generate(
        connector.domain, activity, careplan, practitioner)
    connector.post_message(xml)
    num_messages_after = get_num_messages(careplan.patient.url)
    assert num_messages_after == num_messages_before + 1


def test_messages_for_patient(
        connector, patient, careplan, careplan_on_server):
    '''Get messages for a specific patient.'''
    from koppeltaal.feed import parse
    messages = parse(connector.messages(
        patient_url=careplan.patient.url, summary=True))
    # Because of random_id we know that this patient has exactly one message.
    assert len(list(messages)) == 1


def test_message_for_id(connector, careplan_on_server):
    from koppeltaal.feed import parse
    messages = list(parse(connector.messages(
        summary=True, patient_url=careplan_on_server.patient.url)))
    message_id = messages[0].id
    message_details = connector.message(message_id)
    assert message_id in message_details
    assert careplan_on_server.id in message_details


def test_messages_for_status(connector, patient, careplan, careplan_on_server):
    '''Get messages for a specific status.'''
    from koppeltaal.feed import parse
    messages = list(parse(connector.messages(
        patient_url=careplan.patient.url)))
    assert len(messages) == 1
    id, status = messages[0].id, messages[0].processing_status
    assert status == "New"  # Because not claimed yet.

    messages2 = list(parse(connector.messages(
        processing_status="New",
        patient_url=careplan.patient.url)))
    assert len(messages2) == 1
    # The same message.
    assert messages2[0].id == id

    messages2 = list(parse(connector.messages(
        processing_status="Claimed",
        patient_url=careplan.patient.url)))
    assert len(messages2) == 0


def test_claim(connector, patient, practitioner, careplan, careplan_on_server):
    '''Claim a specific message.'''
    from koppeltaal.feed import parse

    # Get the messages for this patient.
    messages_xml = connector.messages(patient_url=patient.url)
    messages_for_pat = list(parse(messages_xml))
    assert len(messages_for_pat) == 1
    message_info = messages_for_pat[0]
    assert message_info.id is not None
    assert message_info.processing_status == 'New'

    full_message = connector.message(message_info.id)
    # Smoke test.
    assert patient.name.given in full_message

    # Now claim the message.
    connector.message_process(message_info.id, action='claim')

    # The status is "Claimed".
    messages_xml = connector.messages(patient_url=patient.url)
    messages_for_pat = list(parse(messages_xml))
    assert len(messages_for_pat) == 1
    message_info = messages_for_pat[0]
    assert message_info.id is not None
    assert message_info.processing_status == 'Claimed'


def test_success(
        connector, patient, practitioner, careplan, careplan_on_server):
    '''Claim a specific message and mark it as a success.'''
    from koppeltaal.feed import parse

    # Get the messages for this patient.
    messages_xml = connector.messages(patient_url=patient.url)
    messages_for_pat = list(parse(messages_xml))
    assert len(messages_for_pat) == 1
    message_info = messages_for_pat[0]

    # Now claim the message.
    connector.message_process(message_info.id, action='claim')
    connector.message_process(message_info.id, action='success')

    messages_xml = connector.messages(
        patient_url=patient.url, processing_status='New')
    assert len(list(parse(messages_xml))) == 0
    res = connector.message(message_info.id)
    # XXX We could parse this instead of doing a string check.
    assert '<valueCode value="Success" />' in res


def test_cannot_finalize_non_claimed_message(connector):
    '''
    When we try to finalize a message that we hadn't claimed before, this
    should yield an error.
    '''
