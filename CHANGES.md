Changes
=======

1.3.2.2 (2018-01-17)
--------------------

- Make sure to pass a unicode filename to ConfigParser. This prevents a    
  warning under Python 2.7.14.

1.3.2.1 (2018-01-17)
--------------------

- Python 3 compatibility. The adapter now formally supports Python 2.7 and
  Python 3.6 through the `six` compatibility layer..

1.2.1 (2017-10-16)
------------------

- Koppeltaal server does not properly format message headers for
  CreateOrUpdateActivityDefinition, add a fix to still allow those
  messages.

1.2 (2017-08-30)
----------------

- Add Organization resource.

- Add support for careProvider and managingOrganization on Patient
  resource.

- Add support for birthDate, gender and organization on Practitioner
  resource.

- Add a DummyConnector. This has the same API than a connector but
  does not do anything. That's useful when you want to make sure your
  application works, but cannot talk to the Koppeltaal server.

1.1 (2017-05-15)
----------------

- Packaging fixes in preparation for the first public release on
  https://pypi.python.org/pypi.

1.0 (2017-02-17)
----------------

- Add `includearchived` support to list archived `ActivityDefinition`.

- Do not log everything in the console script unless the verbose
  option is used.

1.0b2 (2016-12-14)
------------------

- Skip and ACK messages that originated from "own" endpoint.

- Improve test coverage. Now at 80%.

- Create and update `ActivityDefinition` resources.

- Pass on the sequence of resources in the bundle next to the focal
  resource as part of the `Update()` context manager.

- Improve parsing human name sequences.

- API to Request launch URLs and SSO tokens.

- Option to save retrieved messages to file for introspection.

1.0b1 (2016-07-22)
------------------

- Complete rewrite of the connector code. This includes:

  - Integration hooks for application frameworks (transaction
    management, URL and id generation).

  - Automatic message status handling

  - Resource models

  - Koppeltaal specification-based (de)serialisation of fields

  - Resolving resource references

  - A more complete test suite

  - Improved CLI

  - Compatibility with KT 1.0 and upcoming KT 1.1.1

0.1a1 (2016-06-29)
------------------

- Initial creation.
