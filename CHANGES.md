Changes
=======

1.3.5.9 (2021-01-21)
--------------------

- Fix #61 for `RelatedPerson.Address` cardinality.

1.3.5.8 (2020-11-09)
--------------------

- Add RelatedPerson resource definition and support.

1.3.5.7 (2020-11-03)
--------------------

- Do not fail reporting an OperationOutcomeError for None resources
  (e.g. when sending CarePlanActivityStatus messages).

1.3.5.6 (2020-09-15)
--------------------

- Allows the fetch updates call to optionally add query parametes for Patient
  and event type. See also https://vzvz.gitbook.io/koppeltaal-1-3-architectuur/technologie-architectuur#bericht-ophalen
  for the possible query parameters.

1.3.5.5 (2020-04-28)
--------------------

- Repository cleanups, remove buildout in favor of virtual env, pip and tox.

- Add `HumanName.text` field to the `Name` definition and model.

1.3.5.4 (2019-12-20)
--------------------

- Add the "official" NamingSystem definitions.

- The resource reference from the `MessageHeader` to the so called focal
  resource of the bundle needs to be versioned.

- Have the `InvalidValue` exception report a tiny bit more information.

- Improvements for messages subcommand.

1.3.5.3 (2018-11-16)
--------------------

- Corrected `CarePlanActivityStatus.PercentageCompleted` to accept zero or
  one item.

1.3.5.2 (2018-11-09)
--------------------

- Corrected `Address.line` to accept zero or more items.

- Display errors in command line tool by default (error log level "error").

1.3.5.1 (2018-11-06)
--------------------

- Corrected `Patient.address` to accept zero or more items.

1.3.5 (2018-10-29)
------------------

- Koppeltaal 1.3.5:

  - Added support for the Care Team extension.

  - Verified the requirement on adding versioned resources to message bundle
    works. This requires application integration code to keep track of the
    version of the referenced resources.

  - There's not "first item only" option anymore for fields that are a
    sequence of items. The application integration code needs the handle the
    sequences. This applies to MessageHeaderResponse.data.

  - The data in the response from the Koppeltaal server now contains the new
    versions of all resources that were sent. The application integration code
    needs to keep track of those versions.

  - Added Organization.Address.

  - Fixed several dispay values for codings.

1.3.2.4 (2018-03-12)
--------------------

- Add missing Activity.simple implementation (simple summary of the
  activity details).

- Improve validation errors to be more descriptive.

- In a care plan, change sub activity status from a code to a coding.

1.3.2.3 (2018-02-28)
--------------------

- Fix Python 3 deprecation warnings.

- Add an API to explicitly close the connection to the server.

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
