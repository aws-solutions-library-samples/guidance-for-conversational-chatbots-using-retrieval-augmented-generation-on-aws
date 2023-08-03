#
# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import logging
import json
import helpers
import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']
    return {}

def lambda_handler(event, context):
    logger.info('<help_desk_bot>> Lex event info = ' + json.dumps(event))

    session_attributes = get_session_attributes(event)

    logger.debug('<<help_desk_bot> lambda_handler: session_attributes = ' + json.dumps(session_attributes))
    
    currentIntent = event['sessionState']['intent']['name']
    
    if currentIntent is None:
        response_string = 'Sorry, I didn\'t understand.'
        return helpers.close(session_attributes,currentIntent, 'Fulfilled', {'contentType': 'PlainText','content': response_string})
    intentName = currentIntent
    if intentName is None:
        response_string = 'Sorry, I didn\'t understand.'
        return helpers.close(session_attributes,intentName, 'Fulfilled', {'contentType': 'PlainText','content': response_string})

    # see HANDLERS dict at bottom
    if HANDLERS.get(intentName, False):
        return HANDLERS[intentName]['handler'](event, session_attributes)   # dispatch to the event handler
    else:
        response_string = "The intent " + intentName + " is not yet supported."
        return helpers.close(session_attributes,intentName, 'Fulfilled', {'contentType': 'PlainText','content': response_string})

def hello_intent_handler(intent_request, session_attributes):
    # clear out session attributes to start new
    session_attributes = {}

    response_string = "Hello! How can we help you today?"
    return helpers.close(intent_request,session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

def fallback_intent_handler(intent_request, session_attributes):

    query_string = ""
    #if intent_request.get('inputTranscript', None) is not None:
    query_string += intent_request['transcriptions'][0]['transcription']

    logger.debug('<<help_desk_bot>> fallback_intent_handler(): calling get_kendra_answer(query="%s")', query_string)
        
    kendra_response = helpers.simple_orchestrator(query_string)
    if kendra_response is None:
        response = "Sorry, I was not able to understand your question."
        return helpers.close(intent_request,session_attributes,'Fulfilled', {'contentType': 'PlainText','content': response})
    else:
        logger.debug('<<help_desk_bot>> "fallback_intent_handler(): kendra_response = %s', kendra_response)
        return helpers.close(intent_request,session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': kendra_response})

# list of intent handler functions for the dispatch proccess
HANDLERS = {
    'greeting_intent':              {'handler': hello_intent_handler},
    'FallbackIntent':           {'handler': fallback_intent_handler}
}
