#helper.py
import logging
import json
import pprint
import config
import re
import os
import boto3

from KendraAgent import KendraAgent
from memory import chatMemory
from tools import KendraChatBotTools
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import ContentHandlerBase
from typing import Any, Optional ,Dict
from langchain.llms import Anthropic

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#####################
#This code is usefull to handle input and output from Sagemaker endpoint

class ContentHandler(ContentHandlerBase):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({ "prompt" : prompt, **model_kwargs})
        return input_str.encode('utf-8')
    
    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        #response_json = output.read().decode("utf-8")
        return response_json["completions"][0]['data']['text']

content_handler = ContentHandler()

######################

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

def get_user_message(event):
    return event['transcriptions'][0]['transcription']
    
def get_sessionid(event):
    return event['sessionId']

def is_http_request(event):
    return 'headers' in event

def create_presigned_url(bucket_name, object_name, expiration=120):
    # Choose AWS CLI profile, If not mentioned, it would take default
    #boto3.setup_default_session(profile_name='personal')
    # Generate a presigned URL for the S3 object
    #s3_client = boto3.client('s3',region_name="us-east-1",config=boto3.session.Config(signature_version='s3v4',))
    s3_client = boto3.client('s3',region_name="us-east-1")
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        print(e)
        logging.error(e)
        return "Error"
    # The response contains the presigned URL
    print(response)
    return response

def url_parser(text):
    match = re.search(r'\[source\s*:\s*(?P<url>[^\]]+)\s*\]$',text)
    if match:
        url =match.group('url').strip()
        if url.startswith('s3://'):
            
            s3 = boto3.client('s3')
            bucket_name ,key = url[len('s3://'):].split('/',1)
            #signed_url =s3.generate_presigned_url()
            
            signed_url = create_presigned_url(bucket_name,key)
            #signed_url = url
            file_name = os.path.basename(key)
            return text[:match.start()],signed_url,file_name
            
            
        else:
            return text[:match.start()],None,None
    else:
        return text,None,None


def clear_history(event):
    sessionId =get_sessionid(event)
    chatMemory(sessionId).clear_DynamoDBChatMessageHistory()
    return "conversation history cleared"

#AI handler
def AI_handler(event):
    #print('printing Event : ',event)
    user_message = get_user_message(event)
    sessionId= get_sessionid(event)
    
    llm = Anthropic(
        #config.config.MODEL_ENDPOINT
        anthropic_api_key=config.config.API_KEYS_ANTHROPIC_NAME,
        temperature=0
    )
    
    #llmm =SagemakerEndpoint(
    #    endpoint_name="j2-jumbo-instruct",
    #    region_name="us-east-1", 
    #    model_kwargs={"temperature":0,"maxTokens":1000 ,"numResults": 2},
    #    content_handler=content_handler
    #)
    
    tools = KendraChatBotTools().tools
    memory = chatMemory(sessionId).memory

    kendra_agent = KendraAgent(llm, memory, tools)
    message = kendra_agent.run(input=user_message)
    return url_parser(message)


