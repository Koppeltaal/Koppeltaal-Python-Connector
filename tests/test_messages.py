def test_messages(connector, careplan):
    '''Get messages from the server.'''
    from koppeltaal.message import parse_messages
    messages = parse_messages(connector.messages())
    assert len(messages.entries) > 0


def test_messages_for_patient(connector, careplan):
    '''Get messages for a specific patient.'''
    from koppeltaal.message import parse_messages
    messages = parse_messages(connector.messages(
        patient_url=careplan.patient.url))
    # Because of random_id we know that this patient has exactly one message.
    assert len(messages.entries) == 1


def test_message_for_id(connector):
    '''Get a specific message.'''


def test_claim_message(connector, patient, practitioner, careplan):
    '''Claim a specific message.'''


def test_handle_message_success(connector):
    '''Claim a specific message and process it, tell the server you are done
    with this message.'''


def test_cannot_finalize_non_claimed_message(connector):
    '''
    When we try to finalize a message that we hadn't claimed before, this should
    yield an error.
    '''
