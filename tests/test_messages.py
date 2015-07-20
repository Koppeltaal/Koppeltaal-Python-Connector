def test_messages(connector, patient, practitioner, careplan):
    '''Get messages from the server.'''
    from koppeltaal.message import parse_messages
    from testing import send_create_or_update_careplan_to_server

    def get_num_messages():
        return len(parse_messages(connector.messages(summary=True)).entries)

    # We use the careplan fixture so we know there's at least one message in
    # the mailbox.
    num_messages_before = get_num_messages()
    send_create_or_update_careplan_to_server(
        connector, patient, practitioner, careplan)
    num_messages_after = get_num_messages()
    assert num_messages_after == num_messages_before + 1




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
