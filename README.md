# Koppeltaal Python connector

## Buildout

The dependencies for the koppeltaal python connector is put together using [buildout].

On Linux/OSX, run:

```sh
$ python2.7 bootstrap.py
$ bin/buildout
```

On Windows, run (this works best in a git shell):

```sh
$ C:\Python27\Python.exe bootstrap.py
$ bin\buildout.exe
```

## Tests

We use the [pytest] framework. The tests are run against a Koppeltaal server, for instance:

```sh
$ bin/py.test --server https://edgekoppeltaal.vhscloud.nl
```

## Command line interface

To use the koppeltaal connector command line interface:

```sh
$ bin/koppeltaal --help
```

Arguments:

The first argument to the *koppeltaal* script is the server to connect to, for
example *https://edgekoppeltaal.vhscloud.nl*. The username, password and
domain can be passed in as arguments or taken from *~/.koppeltaal.cfg*. The
format of ~/.koppeltaal.cfg looks like this:

```
[https://edgekoppeltaal.vhscloud.nl]
username = MindDistrict
password = gele-haas (replace with your own)
domain = MindDistrict Kickass
```

If you want to see verbose output, use the *--verbose* flag.

### Metadata / Conformance statement

To retrieve the Conformance statement from the server:

```sh
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl metadata
```

### Activity definition

To get the activity definition from the server:

```sh
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl activities
```

### Messages

To get a list of messages in the mailbox:

```sh
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl messages
```

You can filter on a patient (with *--patient*), or event (with
*--event*) or status (with *--status*):

```sh
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl messages --status New --event CreateOrUpdateCarePlan
```

To get a specific message:

```sh
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl message message_url
```

### Create or update care plan

```sh
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl create_or_update_care_plan --help
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
$ bin/koppeltaal https://edgekoppeltaal.vhscloud.nl create_or_update_care_plan \
KTSTESTGAME \
1 http://test.minddistrict.com/p/1 Claes Vries \
7 http://test.minddistrict.com/cp/7 \
3 http://test.minddistrict.com/pp/3 Joop Smit
```

## Python API

Use the following API in your integration code to talk to a koppeltaal server:

```python
from koppeltaal.connect import Connector

# takes server, username and password as arguments.
c = Connector('https://edgekoppeltaal.vhscloud.nl', 'username', 'password', 'domain')

# metadata from the server, Conformance statement.
c.metadata()

# get all the activity definitions from server.
activities = c.activities()

# get a specific activity definition from server.
activity = c.activity('KTSTESTGAME')

# search for messages in the mailbox.
messages = c.search(status='New', event='CreateOrUpdateCarePlan')

# send an update.
c.send('CreateOrUpdateCarePlan', careplan, patient)
```

[buildout]: http://www.buildout.org
[pytest]: https://pytest.org
