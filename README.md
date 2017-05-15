# Koppeltaal Python connector

## Buildout

The dependencies for the Koppeltaal Python connector is put together using [buildout].

On Linux/OSX, run:

```sh
$ python2.7 bootstrap-buildout.py
$ bin/buildout
```

On Windows, run (this works best in a git shell):

```sh
$ C:\Python27\Python.exe bootstrap-buildout.py
$ bin\buildout.exe
```

## Tests

We use the [pytest] framework. The tests are run against a Koppeltaal server and domain setup specifically for testing the connector code base. This domain is called `edge`:

```sh
$ bin/py.test --server=edge
```

## Command line interface

To use the koppeltaal connector command line interface:

```sh
$ bin/koppeltaal --help
```

Arguments:

The first argument to the *koppeltaal* script is the server to connect to, for
example *edge*. The username, password and
domain can be passed in as arguments or taken from *~/.koppeltaal.cfg*. The
format of ~/.koppeltaal.cfg looks like this:

```
[edge]
url = https://edgekoppeltaal.vhscloud.nl
username = PA@PythonAdapterTesting4Edge
password = <secret here>
domain = PythonAdapterTesting
```

### Metadata / Conformance statement

To retrieve the Conformance statement from the server:

```sh
$ bin/koppeltaal [servername] metadata
```

### Activity definition

To get the activity definition from the server:

```sh
$ bin/koppeltaal [servername] activities
```

### Messages

To get a list of messages in the mailbox:

```sh
$ bin/koppeltaal [servername] messages
```

You can filter on a patient (with *--patient*), or event (with
*--event*) or status (with *--status*):

```sh
$ bin/koppeltaal [servername] messages --status=New --event=CreateOrUpdateCarePlan
```

To get a specific message:

```sh
$ bin/koppeltaal [servername] message [message URL or id]
```

## Python API

Use the following API in your integration code to talk to a Koppeltaal server:

T.B.D.

[buildout]: http://www.buildout.org
[pytest]: https://pytest.org
