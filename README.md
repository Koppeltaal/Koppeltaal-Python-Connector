Koppeltaal Python connector
===========================

“Koppeltaal” (Ducth for "Connect language") is a technical solution based on
the international HL7/FHIR standard. It enables the exchange of e-health
interventions. Koppeltaal enables organizations to connect e-health
interventions from other providers to their own IT environment. With
Koppeltaal organizations can more easily mix and match the best of the
available e-health interventions and applications.

See https://koppeltaal.nl/

This connector acts as an intermediary or adapter between application and framework code and a Koppeltaal server. It is written in the Python programming language.

See https://python.org

This Koppeltaal connector was initially developed by Minddistrict Development B.V. for Stichting Koppeltaal.

Setting up for development
---------------------------

Previously `buildout` was used for setting up the package for development. We now realy on using a *virtual env*, *pip* and a requirements file instead.

Quick start:

```sh
# inside the Koppeltaal-Python-Connector checkout
$ python3.8 -m venv .
$ ./bin/pip install -r requirements -e .
```

Or if you use [pipenv](https://github.com/pypa/pipenv):
```sh
# inside the Koppeltaal-Python-Connector checkout
$ pipenv install -r requirements -e .
```

Tests
-----

We use the [pytest] framework. The tests should be run against the Koppeltaal `edge` server, preferrably in a domain sepcifically setup for running the
tests.

```sh
$ bin/py.test --server=edge
```

The `--server=edge` argument to the test command is the server to connect to when running tests. It is taken from `~/.koppeltaal.cfg`. The format of
`~/.koppeltaal.cfg` looks like this:

```
[edge]
url = https://edgekoppeltaal.vhscloud.nl
username = PA@PythonAdapterTesting4Edge
password = <secret here>
domain = PythonAdapterTesting
```

The name of the configuration section in the `~/.koppeltaal.cfg` file is the name passed to the `--server` argument.

Note how there're two webdriver/selenium tests. They require a Firefox "driver" to be available on your system. For MacOS using brew, this can be installed like so:

```sh
$ brew install geckodriver
```

*Tox* is used for running the test suites for multiple Python versions including 2.7, 3.6, 3.7 and 3.8. Python 2 compatibility is supported throug [six].

Command line interface
----------------------

To use the koppeltaal connector command line interface:

```sh
$ bin/koppeltaal --help
```

Arguments:

The first argument to the *koppeltaal* script is the server to connect to, for
example *edge*. The username, password and domain can be passed in as arguments or taken from `~/.koppeltaal.cfg`.

Metadata / Conformance statement
--------------------------------

To retrieve the Conformance statement from the server:

```sh
$ bin/koppeltaal [servername] metadata
```

Activity definition
-------------------

To get the activity definition from the server:

```sh
$ bin/koppeltaal [servername] activities
```

Messages
--------

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

Python API
----------

Use the following API in your integration code to talk to a Koppeltaal server:

T.B.D.

[buildout]: http://www.buildout.org
[pytest]: https://pytest.org
[six]: http://six.readthedocs.io/
