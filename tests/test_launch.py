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


def test_launch_patient(
        connector, activity, careplan_on_server, patient, browser):
    launch_url = connector.launch(activity.id, patient.url, patient.url)

    # The launch URL points to the game location, with a iss= query parameter
    # pointing back to the koppeltaal server.
    parsed_launch_url = urlparse.urlparse(launch_url)
    assert urlparse.parse_qs(
        parsed_launch_url.query)['iss'][0].startswith(connector.server)

    browser.get(launch_url)
    wait_for_game(browser)

    # After some back and forth, the browser points to the game.
    parsed_game_url = urlparse.urlparse(browser.current_url)
    assert 'ranjgames.com' in parsed_game_url.netloc
    assert 'test.html' in parsed_game_url.path

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

    # After some back and forth, the browser points to the game.
    parsed_game_url = urlparse.urlparse(browser.current_url)
    assert 'ranjgames.com' in parsed_game_url.netloc
    assert 'test.html' in parsed_game_url.path

    # There is a 'login with oauth' button in the page, let's see what that
    # does.
    assert browser.find_element_by_id('patientReference').text == ''
    assert browser.find_element_by_id('userReference').text == ''
    login_with_oauth(browser)
    assert browser.find_element_by_id('patientReference').text == patient.url
    assert browser.find_element_by_id('userReference').text == practitioner.url


# Send some messages from the game.
