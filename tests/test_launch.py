import urlparse
import selenium.webdriver.support.wait
import selenium.webdriver.support.expected_conditions as EC


def wait_for_game(browser):
    # wait until the page redirect dance is over.
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(lambda d: 'test.html' in d.current_url)


def login_with_oauth(browser):
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'log in with oauth'][0].click()
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            EC.text_to_be_present_in_element(
                ('id', 'authorizationOutput'), 'access_token'))


def request_care_plan(browser):
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'request care plan'][0].click()
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            EC.text_to_be_present_in_element(
                ('id', 'carePlanOutput'), 'reference'))


def test_launch_patient(
        connector, activity, careplan_on_server, patient, browser):
    launch_url = connector.launch(activity.id, patient.url, patient.url)

    parsed_launch_url = urlparse.urlparse(launch_url)
    assert urlparse.parse_qs(
        parsed_launch_url.query)['iss'][0].startswith(connector.server)

    browser.get(launch_url)
    wait_for_game(browser)

    # There is a 'login with oauth' button in the page, let's see what that
    # does.
    assert browser.find_element_by_id('patientReference').text == ''
    assert browser.find_element_by_id('userReference').text == ''

    login_with_oauth(browser)
    assert browser.find_element_by_id('patientReference').text == patient.url
    assert browser.find_element_by_id('userReference').text == patient.url


def test_launch_practitioner(
        connector, activity, careplan_on_server, patient, practitioner,
        browser):
    launch_url = connector.launch(activity.id, patient.url, practitioner.url)
    browser.get(launch_url)
    wait_for_game(browser)

    # There is a 'login with oauth' button in the page, let's see what that
    # does.
    assert browser.find_element_by_id('patientReference').text == ''
    assert browser.find_element_by_id('userReference').text == ''

    login_with_oauth(browser)
    assert browser.find_element_by_id('patientReference').text == patient.url
    assert browser.find_element_by_id('userReference').text == practitioner.url


def set_domain(browser):
    browser.find_element_by_id("domain").clear()
    # XXX Find the domain in the settings.
    browser.find_element_by_id("domain").send_keys("MindDistrict")
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'set new domain'][0].click()


def post_sub_activities(browser):
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'post sub activities'][0].click()
    selenium.webdriver.support.wait.WebDriverWait(
        browser, 10).until(
            EC.text_to_be_present_in_element(
                ('id', 'carePlanOutput'), 'scenario_'))


def post_update(browser):
    [b for b in browser.find_elements_by_tag_name('button') if
        b.text == 'post update'][0].click()


def test_send_message_from_game_to_server(
        connector, activity, careplan_on_server, patient, browser):
    from koppeltaal.feed import parse

    launch_url = connector.launch(activity.id, patient.url, patient.url)

    # The message to koppeltaal server needs to be acked.
    messages = list(parse(connector.messages(
        processing_status="New", patient_url=patient.url)))
    assert len(messages) == 1

    connector.message_process(messages[0].id, action='claim')
    connector.message_process(messages[0].id, action='success')

    # Acked indeed.
    messages_again = list(parse(connector.messages(
        processing_status="New", patient_url=patient.url)))
    assert len(messages_again) == 0

    browser.get(launch_url)
    wait_for_game(browser)
    set_domain(browser)
    login_with_oauth(browser)
    request_care_plan(browser)
    post_sub_activities(browser)
    messages_after_javascript = list(parse(connector.messages(
        processing_status="New", patient_url=patient.url)))
    assert len(messages_after_javascript) == 1

    message_details = connector.message(messages_after_javascript[0].id)
    assert 'CarePlan#SubActivity' in message_details
