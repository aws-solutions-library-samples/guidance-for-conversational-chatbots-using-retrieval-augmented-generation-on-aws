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
from PyPDF2 import PdfReader
from io import BytesIO
import boto3
from typing import Type
import config

class Kendraa(Docstore):
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

    def getTextFromPDF(self,pageNumber,bucket,key):
        obj = self.s3_client.get_object(Bucket=bucket, Key=key)
        reader = PdfReader(BytesIO(obj["Body"].read()))
        pageObj = reader.pages[pageNumber]
        return pageObj.extract_text()

    #def search(self, query : str ) -> str, Document]:
    def search(self, query : str ) -> str:
        """Try to search for a document in Kendra Index""
        
        """
        response = self.kendra_client.query(
            QueryText=query,
            IndexId=self.kendra_index_id,
            #QueryResultTypeFilter='DOCUMENT',
            )
        first_result_type = ''
        #print("Response :",response['ResultItems'][0])
        
        try:
            first_result_type = response['ResultItems'][0]['Type']
        except KeyError:
            return None
        if first_result_type=="ANSWER":
            print("Found Document Excerpt")
            document_title = response['ResultItems'][0]['DocumentTitle']['Text']
            #document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
            document_excerpt_text = response['ResultItems'][0]["AdditionalAttributes"][0]["Value"]["TextWithHighlightsValue"]["Text"]
            #pageNumber = self.parseResponse(response)
            #print("Document_title: ",document_title)
            #print("Page Number:",pageNumber + 1 )
            sourceURI = response['ResultItems'][0]['DocumentId']
            #print(document_excerpt_text + sourceURI)
            return( document_excerpt_text + " [source :"+sourceURI+"]")
        
        elif first_result_type == 'DOCUMENT':
            #pageNumber = self.parseResponse(response)
            #print("Page Number:",pageNumber +1)
            sourceURI = response['ResultItems'][0]['DocumentId']
            document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
            return( document_excerpt_text + " [source :"+sourceURI+"]")
        
        else:
            return f"No Results returned for query :{query}"

class KendraChatBotTools():
    kendra_docstore = Kendraa(kendra_index_id =config.config.KENDRA_INDEX,region_name=config.config.KENDRA_REGION)
    
    def __init__(self) -> None:
        self.tools = [
            Tool(
                name="search",
                func=self.kendra_docstore.search,
                description="This tool should be used to answer financial question realted to Amazon 10K such as risks,stocks, audits and risk management"

                )
        ]
        #description="This tool should be used to answer financial questions related contents of 10K such as revenue,stocks,risks,board of directors, employee count etc."
        #description="Ask questions to this tool to get relavent document excerpts

tools = KendraChatBotTools().tools
