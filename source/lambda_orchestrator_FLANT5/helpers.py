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

import boto3
import time
import logging
import json
import pprint
import os
import config
import boto3
from io import BytesIO
#from typing import Any, Optional


logger = logging.getLogger()
logger.setLevel(logging.INFO)

kendra_client = boto3.client('kendra')
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")

model_endpoint=config.config.MODEL_ENDPOINT
"j2-jumbo-instruct"


def close(intent_request,session_attributes,fulfillment_state, message):

    response = {
                    'sessionState': {
                        'sessionAttributes': session_attributes,
                		'dialogAction': {
                            'type': 'Close'
                        },
                        'intent': intent_request['sessionState']['intent']
                        },
                    'messages': [message],
                    'sessionId': intent_request['sessionId']
                }
    response['sessionState']['intent']['state'] = fulfillment_state
    
    #if 'requestAttributes' in intent_request :
    #    response['requestAttributes']   =  intent_request["requestAttributes"]
        
    logger.info('<<help_desk_bot>> "Lambda fulfillment function response = \n' + pprint.pformat(response, indent=4)) 

    return response

def model_input_transform_fn(prompt):
        #parameters = {
        #    "num_return_sequences": 1, "max_new_tokens": 100, "temperature": 0.8, "top_p": 0.1,
        #}
        parameter_payload = {"text_inputs": prompt}
        return json.dumps(parameter_payload).encode("utf-8")

def get_prediction_llm(question,context):
    prompt = f"""Answer the question based ONLY on the contex provided. Do not answer if context is not relavent to question 
                question: {question} context: {context}
                answer: """
    print(prompt)
    try:
        response = sagemaker_runtime.invoke_endpoint(
                    EndpointName=model_endpoint,
                    Body=model_input_transform_fn(prompt),
                    ContentType="application/json",
                    )
    except Exception as e:
        print(e)
        raise ValueError(f"Error raised by inference endpoint: {e}")
        
    response_json = json.loads(response["Body"].read().decode("utf-8"))
    text = response_json['generated_texts'][0]
    return text

def get_kendra_answer(question):
    try:
        KENDRA_INDEX = config.config.KENDRA_INDEX
    except KeyError:
        return 'Configuration error - please set the Kendra index ID in the environment variable KENDRA_INDEX.'
    
    try:
        response = kendra_client.query(IndexId=KENDRA_INDEX, QueryText=question)
    except:
        return None
    
    logger.debug('<<help_desk_bot>> get_kendra_answer() - response = ' + json.dumps(response)) 
    #
    # determine which is the top result from Kendra, based on the Type attribue
    #  - QUESTION_ANSWER = a result from a FAQ: just return the FAQ answer
    #  - ANSWER = text found in a document: return the text passage found in the document plus a link to the document
    #  - DOCUMENT = link(s) to document(s): check for several documents and return the links
    #
    first_result_type = ''
    try:
        if response['TotalNumberOfResults']!=0:
            first_result_type = response['ResultItems'][0]['Type']
        else:
            return None
    except KeyError:
        return None

    if first_result_type == 'QUESTION_ANSWER':
        try:
            faq_answer_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
        except KeyError:
            faq_answer_text = "Sorry, I could not find an answer in our FAQs."

        return faq_answer_text

    elif first_result_type == 'ANSWER':
        # return the text answer from the document, plus the URL link to the document
        try:
            document_title = response['ResultItems'][0]['DocumentTitle']['Text']
            document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
            document_url = response['ResultItems'][0]['DocumentURI']
            answer_text = "Here's an excerpt from a document ("
            answer_text += "<" + document_url + "|" + document_title + ">"
            answer_text += ") that might help:\n\n" + document_excerpt_text + "...\n"            
        except KeyError:
            answer_text = "Sorry, I could not find the answer in our documents."
        return get_prediction_llm(question,answer_text)

    elif first_result_type == 'DOCUMENT':
        # assemble the list of document links
        document_list = "Here are some documents you could review:\n"
        for item in response['ResultItems']:
            document_title = None
            document_url = None
            if item['Type'] == 'DOCUMENT':
                if item.get('DocumentTitle', None):
                    if item['DocumentTitle'].get('Text', None):
                        document_title = item['DocumentTitle']['Text']
                if item.get('DocumentId', None):
                    document_url = item['DocumentURI']
            
            if document_title is not None:
                document_list += '-  <' + document_url + '|' + document_title + '>\n'

        return get_prediction_llm(question,document_list)
    
    else:
        return None

def simple_orchestrator(question):
    
    #Get answers from Amazon Kendra
    context = get_kendra_answer(question)
    
    #Get predictions from LLM based on questuion and Kendra results
    llm_response = get_prediction_llm(question,context)
    
    return llm_response
    
    
    
    
