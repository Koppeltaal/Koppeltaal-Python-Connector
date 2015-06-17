# Koppeltaal Python connector

## Buildout

The dependencies for the koppeltaal python connector is put together using [buildout].

Run:

```sh
$ python2.7 bootstrap.py
$ bin/buildout
```

## Tests

We use the [pytest] framework. The tests are run against a Koppeltaal server, for instance:

```sh
$ bin/py.test --server https://testconnectors.vhscloud.nl
```

## Command line interface

To use the koppeltaal connector command line interface:

```sh
$ bin/koppeltaal --help
```

Arguments:

The first argument to the *koppeltaal* script is the server to connect to, for
example *https://testconnectors.vhscloud.nl*. The username and password can be
passed in as arguments or taken from *~/.koppeltaal.cfg*. The format of
~/.koppeltaal.cfg looks like this:

```
[https://testconnectors.vhscloud.nl]
username = MindDistrict
password = gele-haas (replace with your own)
domain = MindDistrict Kickass
```

If you want to see verbose output, use the *--verbose* flag.

### Test authentication

To test whether you have the proper username+password for the server you want
to work with, use the test_authentication command. This returns status code 1
in case of failure, 0 in case of success.

```sh
$ bin/koppeltaal https://testconnectors.vhscloud.nl test_authentication  # uses the values from ~/.koppeltaal.cfg
$ bin/koppeltaal https://testconnectors.vhscloud.nl --username=foo --password=bar test_authentication  # Returns 1
```

### Activity definition

To get the activity definition from the server:

```sh
$ bin/koppeltaal https://testconnectors.vhscloud.nl activity_definition
```
This returns the raw XML, not very useful.

### Create or update care plan

```sh
$ bin/koppeltaal https://testconnectors.vhscloud.nl create_or_update_care_plan --help
```

To send a new careplan to the server, you need these arguments:

- activity_id
- patient_id
- patient_url
- patient_given_name
- patient_family_name
- careplan_id
- careplan_url
- practitioner_id
- practitioner_url
- practitioner_given_name
- practitioner_family_name

For example:

```sh
$ bin/koppeltaal https://testconnectors.vhscloud.nl create_or_update_care_plan \
  "MindDistrict Kickass" RANJKA \
  1 http://test.minddistrict.com/p/1 Claes Vries \
  7 http://test.minddistrict.com/cp/7 \
  3 http://test.minddistrict.com/pp/3 Joop Smit
```

## Python API

Use the following API in your integration code to talk to a koppeltaal server:

```python
from koppeltaal.connect import Connector

# takes server, username and password as arguments.
c = Connector('https://testconnectors.vhscloud.nl', 'foo', 'bar')

# metadata from the server, Conformance statement.
c.metadata()

# test authentication
c.test_authentication()

# get Activity definitions from server. Returns XML.
xml = c.activity_definition()
# use koppeltaal.activity_definition.activities to parse the XML feed.
from koppeltaal.activity_definition import activities
act = activities(xml)

# Create or update a care plan.
from koppeltaal.create_or_update_care_plan import generate
# Generate the XML feed to be sent to the server.
stanza = generate(domain, activity, patient, careplan, practitioner)
# Send to the server.
c.create_or_update_care_plan(stanza)
```

[buildout]: http://www.buildout.org
[pytest]: https://pytest.org
