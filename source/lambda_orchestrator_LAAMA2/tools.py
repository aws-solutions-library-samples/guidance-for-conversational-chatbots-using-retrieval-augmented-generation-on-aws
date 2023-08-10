# tool.py
from langchain.agents.tools import Tool
from langchain.agents import load_tools
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import requests
import os
import pprint
pp = pprint.PrettyPrinter(depth=2)
from langchain.docstore.base import Docstore
from langchain.docstore.document import Document
import boto3
from io import BytesIO
import boto3
from typing import Type
import config

#Retreive API
class Kendra(Docstore):
    """Wrapper around Kendra API."""

    def __init__(self,kendra_index_id :str, region_name:str) -> None:
        """Check that boto3 package is installed."""
        
        self.used = False
        self.URL = ""
        
        try:
            import boto3
            self.kendra_client = boto3.client("kendra",region_name=region_name)
            self.s3_client = boto3.client("s3")
            self.kendra_index_id = kendra_index_id
            
        except ImportError:
            raise ValueError(
                "Could not import boto3 python package. "
                "Please it install it with `pip install boto3`."
            )

    def parseResponse(self,response):
        for each_loop in response['ResultItems'][0]['DocumentAttributes']:
            if (each_loop['Key']=='_excerpt_page_number'):
                pagenumber = each_loop['Value']['LongValue'] -1   
        return pagenumber
    
    def parseBucketandKey(self,SourceURI):
        return (SourceURI.split('/', 3)[2],SourceURI.split('/', 3)[3])


    #def search(self, query : str ) -> str, Document]:
    def search(self, query : str ) -> str:
        """Try to search for a document in Kendra Index""
        
        """
        try:
            page_size = 2
            page_number = 1

            result =  self.kendra_client.retrieve(
                    IndexId = self.kendra_index_id,
                    QueryText = query,
                    PageSize = page_size,
                    PageNumber = page_number)
        except:
            return "RELAVENT PASSAGES NOT FOUND"

        # Concatinating the results from Kendra Retreive API 
        # https://docs.aws.amazon.com/kendra/latest/dg/searching-retrieve.html
        context =""
        for retrieve_result in result["ResultItems"]:
            context =context +'['
            context = context + "Title: " + str(retrieve_result["DocumentTitle"] + ", URI: " + str(retrieve_result["DocumentURI"]) +", Passage content: " + str(retrieve_result["Content"]))
            context =context + '] '
        return context


class KendraChatBotTools():
    kendra_docstore = Kendra(kendra_index_id =config.config.KENDRA_INDEX,region_name=config.config.KENDRA_REGION)
    
    def __init__(self) -> None:
        self.tools = [
            Tool(
                name="search",
                func=self.kendra_docstore.search,
                description="This tool should be used to search and answer  question "

                )
        ]
 

tools = KendraChatBotTools().tools
