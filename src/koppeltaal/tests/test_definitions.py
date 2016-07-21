import datetime
import mock
import pytest
import koppeltaal.definitions
import koppeltaal.fhir.packer
import koppeltaal.fhir.resource
import koppeltaal.models
import zope.interface.verify


@pytest.fixture
def packer():
    return koppeltaal.fhir.packer.Packer(
        mock.MagicMock(spec=koppeltaal.fhir.resource.Resource),
        mock.MagicMock(return_value='https://example.com/dummy/dummy'))


def test_unpack_name(packer):
    name = packer.unpack(
        {'given': [u'Napoleon'],
         'family': [u'Bonaparte'],
         'use': u'official'},
        koppeltaal.definitions.Name)

    assert zope.interface.verify.verifyObject(
        koppeltaal.definitions.Name, name)
    assert name.given == u'Napoleon'
    assert name.family == u'Bonaparte'
    assert name.use == 'official'

    with pytest.raises(koppeltaal.interfaces.InvalidCode):
        packer.unpack(
            {'given': [u'Napoleon'],
             'family': [u'Bonaparte'],
             'use': u'cool name'},
            koppeltaal.definitions.Name)

    with pytest.raises(koppeltaal.interfaces.InvalidValue):
        packer.unpack(
            {'given': u'Napoleon',
             'family': [u'Bonaparte'],
             'use': u'official'},
            koppeltaal.definitions.Name)

    with pytest.raises(koppeltaal.interfaces.InvalidValue):
        packer.unpack(
            {'given': [u'Napoleon'],
             'family': 42,
             'use': u'official'},
            koppeltaal.definitions.Name)


def test_pack_name(packer):
    name1 = packer.pack(
        koppeltaal.models.Name(
            given=u'Napoleon',
            family=u'Bonaparte',
            use='old'),
        koppeltaal.definitions.Name)

    assert name1 == {
        'family': ['Bonaparte'],
        'given': ['Napoleon'],
        'id': mock.ANY,
        'use': 'old'}

    name2 = packer.pack(
        koppeltaal.models.Name(
            given=u'Nathan'),
        koppeltaal.definitions.Name)

    assert name2 == {'given': ['Nathan'], 'id': mock.ANY, 'use': 'official'}

    with pytest.raises(koppeltaal.interfaces.InvalidResource):
        packer.pack(
            'Napoleon',
            koppeltaal.definitions.Name)

    with pytest.raises(koppeltaal.interfaces.InvalidValue):
        packer.pack(
            koppeltaal.models.Name(
                given=u'Napoleon',
                family=u'Bonaparte',
                use='cool name'),
            koppeltaal.definitions.Name)


def test_pack_patient(packer):
    patient1 = packer.pack(
        koppeltaal.models.Patient(
            active=True,
            age=42,
            name=koppeltaal.models.Name(
                given=u'Paul',
                family=u'Roger',
                use='official'),
            gender='M'),
        koppeltaal.definitions.Patient)

    assert patient1 == {
        'active': True,
        'extension': [
            {'url': 'http://ggz.koppeltaal.nl/fhir/Koppeltaal/Patient#Age',
             'valueInteger': 42}],
        'id': mock.ANY,
        'gender': {'coding': [
            {'code': 'M',
             'display': 'M',
             'system': 'http://hl7.org/fhir/v3/AdministrativeGender'}]},
        'name': [
            {'id': mock.ANY,
             'given': ['Paul'],
             'family': ['Roger'],
             'use': 'official'}]}

    patient2 = packer.pack(
        koppeltaal.models.Patient(
            birth_date=datetime.datetime(1976, 6, 1, 12, 34),
            contacts=[
                koppeltaal.models.Contact(
                    system='email',
                    value=u'petra@example.com',
                    use='home')],
            identifiers=[
                koppeltaal.models.Identifier(
                    system=u'http://fhir.nl/fhir/NamingSystem/bsn',
                    value=u'640563569',
                    use='official')],
            name=koppeltaal.models.Name(
                given=u'Petra',
                use='temp'),
            gender='F'),
        koppeltaal.definitions.Patient)

    assert patient2 == {
        'birthDate': '1976-06-01T12:34:00',
        'gender': {'coding': [
             {'code': 'F',
              'display': 'F',
              'system': 'http://hl7.org/fhir/v3/AdministrativeGender'}]},
        'id': mock.ANY,
        'identifier': [
             {'id': mock.ANY,
              'system': 'http://fhir.nl/fhir/NamingSystem/bsn',
              'value': '640563569',
              'use': 'official'}],
        'name': [
            {'id': mock.ANY,
             'given': ['Petra'],
             'use': 'temp'}],
        'telecom': [
            {'id': mock.ANY,
             'system': 'email',
             'value': 'petra@example.com',
             'use': 'home'}]}
