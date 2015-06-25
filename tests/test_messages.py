

def test_messages(connector):
    '''Get messages from the server.'''


def test_messages_for_patient(connector):
    '''Get messages for a specific patient.'''


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
