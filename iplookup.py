"""
This skill is designed to take an IP address and perform a Geo lookup. 

This product includes GeoLite2 data created by MaxMind, available from
http://www.maxmind.com
"""

from __future__ import print_function
import geoip2.database
import ipaddress

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "IP Geo Lookup - " + title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the IP GeoLocator service. " \
                    "You can say things like: " \
                    "where is eight. dot eight. dot eight. dot eight. located. " \
                    "or, lookup four. dot four. dot four. dot four."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please say a command. You can say things like" \
                    "where is eight. dot eight. dot eight. dot eight. located. " \
                    "or, lookup four. dot four. dot four. dot four."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_help_request():
    session_attributes = {}
    card_title = "Help"
    speech_output = "You can say things like: " \
                    "where is eight. dot eight. dot eight. dot eight. located. " \
                    "or, lookup four. dot four. dot four. dot four."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please say a command. You can say things like" \
                    "where is eight. dot eight. dot eight. dot eight. located. " \
                    "or, lookup four. dot four. dot four. dot four."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Goodbye!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def error_private_address():
    card_title = "Private Address"
    speech_output = "Sorry, you have requested an address in a private network. " \
                    "Please try again with a public address."
    # Setting this to true ends the session and exits the skill.
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def LookupCity(ip):
    reader = geoip2.database.Reader('./GeoLite2-City.mmdb')
    card_title = ip
    session_attributes = {}
    try:
        result = reader.city(ip)
        should_end_session = True
        speech_output = "That address is in " + result.city.name + ", " + result.subdivisions.most_specific.name + ", " + result.country.name
        reprompt_text = None
    except geoip2.errors.AddressNotFoundError:
        should_end_session = False
        speech_output = "Sorry, that address wasn't found in the database. " \
                        "Please try your command again with a different address."
        reprompt_text = "Please try your command again with a different address."
    except ValueError:
        should_end_session = False
        speech_output = "Sorry, that doesn't appear to be a valid request. " \
                        "Please try your command again with a different address."
        reprompt_text = "Please try your command again with a different address."
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "LookupCity"
        intent_slots = intent_request['intent']['slots']
        ip = ("%s.%s.%s.%s" % (intent_slots['One']['value'], intent_slots['Two']['value'], intent_slots['Three']['value'], intent_slots['Four']['value']))
        ip_test = ipaddress.IPv4Address(ip)
        private_ip = ip_test.is_private
        if private_ip == False:
            return LookupCity(ip)
        elif private_ip == True:
            return error_private_address()
    if intent_name == "AMAZON.HelpIntent"
        return handle_help_request()
    if intent_name == "AMAZON.StopIntent"
        return on_session_ended()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return handle_session_end_request()

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

