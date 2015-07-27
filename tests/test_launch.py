import urlparse
import selenium.webdriver


def test_launch_patient(connector, activity, careplan_on_server, patient):
    launch_url = connector.launch(activity.id, patient.url, patient.url)

    # The launch URL points to the game location, with a iss= query parameter
    # pointing back to the koppeltaal server.
    parsed_launch_url = urlparse.urlparse(launch_url)
    assert urlparse.parse_qs(
        parsed_launch_url.query)['iss'][0].startswith(connector.server)

    browser = selenium.webdriver.Firefox()
    browser.get(launch_url)

    # wait until the page redirect dance is over.
    from selenium.webdriver.support.wait import WebDriverWait
    WebDriverWait(browser, 10).until(lambda d: 'test.html' in d.current_url)

    # After some back and forth, the browser points to the game.
    parsed_game_url = urlparse.urlparse(browser.current_url)
    assert 'ranjgames.com' in parsed_game_url.netloc
    assert 'test.html' in parsed_game_url.path

    # XXX Move to fixture, don't want to think about this here.
    browser.quit()


# Send some messages from the game.
# Log in as practitioner.
