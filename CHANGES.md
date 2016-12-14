Changes
=======

1.0b3 (unreleased)
------------------

- Nothing changed yet.


1.0b2 (2016-12-14)
------------------

- Skip and ACK messages that originated from "own" endpoint.

- Improve test coverage. Now at 80%.

- Create and update `ActivityDefinition` resources.

- Pass on the sequence of resources in the bundle next to the focal resource as part of the `Update()` context manager.

- Improve parsing human name sequences.

- API to Request launch URLs and SSO tokens.

- Option to save retrieved messages to file for introspection.

1.0b1 (2016-07-22)
------------------

- Complete rewrite of the connector code. This includes:

  - Integration hooks for application frameworks (transaction management, URL and id generation).

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
