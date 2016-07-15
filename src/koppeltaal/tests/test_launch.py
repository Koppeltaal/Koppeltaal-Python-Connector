# import urlparse
# import selenium.webdriver.support.wait
# import selenium.webdriver.support.expected_conditions as EC


# def wait_for_game(browser):
#     # wait until the page redirect dance is over.
#     selenium.webdriver.support.wait.WebDriverWait(
#         browser, 10).until(lambda d: 'test.html' in d.current_url)


# def login_with_oauth(browser):
#     [b for b in browser.find_elements_by_tag_name('button') if
#         b.text == 'log in with oauth'][0].click()
#     selenium.webdriver.support.wait.WebDriverWait(
#         browser, 10).until(
#             EC.text_to_be_present_in_element(
#                 ('id', 'authorizationOutput'), 'access_token'))


# def request_care_plan(browser):
#     [b for b in browser.find_elements_by_tag_name('button') if
#         b.text == 'request care plan'][0].click()
#     selenium.webdriver.support.wait.WebDriverWait(
#         browser, 10).until(
#             EC.text_to_be_present_in_element(
#                 ('id', 'carePlanOutput'), 'reference'))


# def test_launch_patient(
#         connector, activity, careplan_on_server, patient, browser):
#     import koppeltaal

#     launch_url = connector.launch(activity, patient, patient)
#     parsed_launch_url = urlparse.urlparse(launch_url)
#     assert urlparse.parse_qs(
#         parsed_launch_url.query)['iss'][0].startswith(connector.server)

#     # There is a 'login with oauth' button in the page, let's see what that
#     # does.
#     browser.get(launch_url)
#     wait_for_game(browser)
#     assert browser.find_element_by_id('patientReference').text == ''
#     assert browser.find_element_by_id('userReference').text == ''

#     login_with_oauth(browser)
#     assert browser.find_element_by_id('patientReference').text == \
#         koppeltaal.url(patient)
#     assert browser.find_element_by_id('userReference').text == \
#         koppeltaal.url(patient)


# def test_launch_practitioner(
#         connector, activity, careplan_on_server, patient, practitioner,
#         browser):
#     import koppeltaal

#     # There is a 'login with oauth' button in the page, let's see what that
#     # does.
#     launch_url = connector.launch(activity, patient, practitioner)
#     browser.get(launch_url)
#     wait_for_game(browser)
#     assert browser.find_element_by_id('patientReference').text == ''
#     assert browser.find_element_by_id('userReference').text == ''

#     login_with_oauth(browser)
#     assert browser.find_element_by_id('patientReference').text == \
#         koppeltaal.url(patient)
#     assert browser.find_element_by_id('userReference').text == \
#         koppeltaal.url(practitioner)


# def set_domain(browser):
#     browser.find_element_by_id("domain").clear()
#     # XXX Find the domain in the settings.
#     browser.find_element_by_id("domain").send_keys("MindDistrict")
#     [b for b in browser.find_elements_by_tag_name('button') if
#         b.text == 'set new domain'][0].click()


# def post_sub_activities(browser):
#     [b for b in browser.find_elements_by_tag_name('button') if
#         b.text == 'post sub activities'][0].click()
#     selenium.webdriver.support.wait.WebDriverWait(
#         browser, 10).until(
#             EC.text_to_be_present_in_element(
#                 ('id', 'carePlanOutput'), 'scenario_'))


# def post_update(browser):
#     [b for b in browser.find_elements_by_tag_name('button') if
#         b.text == 'post update'][0].click()


# def test_send_message_from_game_to_server(
#         connector, activity, careplan_on_server, patient, browser):
#     import koppeltaal.interfaces
#     from koppeltaal.feed import parse

#     launch_url = connector.launch(activity, patient, patient)

#     # The message to koppeltaal server needs to be acked.
#     headers = list(parse(
#         connector.messages(
#             patient=patient,
#             processing_status=koppeltaal.interfaces.STATUS_NEW)))
#     assert len(headers) == 1

#     connector.claim(headers[0].__version__)
#     connector.success(headers[0].__version__)

#     # Acked indeed.
#     headers2 = list(parse(
#         connector.messages(
#             patient=patient,
#             processing_status=koppeltaal.interfaces.STATUS_NEW)))
#     assert len(headers2) == 0

#     browser.get(launch_url)
#     wait_for_game(browser)
#     set_domain(browser)
#     login_with_oauth(browser)
#     request_care_plan(browser)
#     post_sub_activities(browser)
#     headers3 = list(parse(
#         connector.messages(
#             patient=patient,
#             processing_status=koppeltaal.interfaces.STATUS_NEW)))
#     assert len(headers3) == 1

#     message = connector.message(headers3[0].__version__)
#     assert 'CarePlan#SubActivity' in message
