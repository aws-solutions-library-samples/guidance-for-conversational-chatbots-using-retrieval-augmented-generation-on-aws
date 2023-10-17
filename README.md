# Guidance for Conversational Chatbots using Retrieval Augmented Generation (RAG) on AWS

## Contents

1. [Overview](#1-overview)
2. [Architecture Details](#2-architecture-details)
3. [Disclaimer](#3-disclaimer)
4. [Prerequisites](#4-prerequisites)
5. [Quick Start](#5-quick-start) 
6. [Advanced Configuration](#6-advanced-configuration)  
    6.1. [Optional CloudFormation Parameters](#61-optional-cloudformation-parameters)      
7. [Module Information](#7-module-information)  
    7.1 [LangChain](#71-langChain)
    7.2 [Cloudfront](#72-cloudfront)
8. [FAQ](#8-faq)
9. [Security](#9-security)
10. [License](#10-license)

-----

## 1. Overview

In this implementation we demonstrate how to implement a RAG workflow by combining the capabilities of Amazon Kendra with LLMs to create state-of-the-art GenAI ChatBot providing conversational experiences over your enterprise content. 

To restrict the GenAI application responses to company data only, we need to use a technique called Retrieval Augmented Generation (RAG). An application using the RAG approach retrieves information most relevant to the user’s request from the enterprise knowledge base or content, bundles it as context along with the user’s request as a prompt, and then sends it to the LLM to get a GenAI response. LLMs have limitations around the maximum word count for the input prompt, therefore choosing the right passages among thousands or millions of documents in the enterprise, has a direct impact on the LLM’s accuracy.


In this particular repository we are going to provide implementation details to deploy a serverless chatbot which can scale to several users, maintain conversational memory, provide detailed links, variety of orchestrators and also provides multiple ways of Lambda implementation; simple and Advanced Agents implemetation, Query rephrasing or disambiguation
-----

## 2. Architecture Details
![RAG Architecture](assets/pic/RAG_Kendra.png?raw=true "RAG with Amazon Kendra")

The workflow includes the following steps:

1. Financial documents and agreements are stored on Amazon S3, and ingested to an Amazon Kendra index using the S3 data source connector.

2. The LLM is hosted on a SageMaker endpoint.

3. An Amazon Lex chatbot is used to interact with the user via the Amazon Lex web UI. Lex UI can leverage cognito to authentice users.

4. The Amazon DynamoDB is used to hold conversational memory.

5. The solution uses an AWS Lambda function with LangChain to orchestrate between Amazon Kendra, Amazon DynamoDB, Amazon Lex, and the LLM.

6. When users ask the Amazon Lex chatbot for answers from a financial document, Amazon Lex calls the LangChain orchestrator to fulfill the request.

7. Based on the query, the LangChain orchestrator pulls the relevant financial records and paragraphs from Amazon Kendra or pull the information from conversational memory in DynamoDB.

8. The LangChain orchestrator provides these relevant records to the LLM along with the query and relevant prompt to carry out the required activity.

9. The LLM processes the request from the LangChain orchestrator and returns the result.

10. The LangChain orchestrator gets the result from the LLM and sends it to the end-user through the Amazon Lex chatbot.

## 3. Disclaimer
1. When selecting websites to index, you must adhere to the Amazon Acceptable Use Policy and all other Amazon terms. Remember that you must only use Amazon Kendra Web Crawler to index your own web pages, or web pages that you have authorization to index. To learn how to stop Amazon Kendra Web Crawler from indexing your website(s), please see Configuring the robots.txt file for Amazon Kendra Web Crawler.
Abusing Amazon Kendra Web Crawler to aggressively crawl websites or web pages you don't own is not considered acceptable use.

    Acceptable usage Policy : 
    https://docs.aws.amazon.com/kendra/latest/dg/data-source-web-crawler.html
    https://github.com/aws-samples/aws-lex-web-ui/tree/master

2. If you are using Lex Web UI always secure your chat UI with Authentication by setting .
![Cognito](assets/pic/cognito.PNG?raw=true "Cognito")

3. Place to help with this in case of RAG use case is to use lower number of max documents, say 1 because Huggingface has a smaller token limit.
Apart from that, currently we expect the user to be responsible for the token limit per the model they select. But we're considering options like rolling window of conversation, so we removed old chat conversations from the history - this would then be an additional option in the rapid-ai wizard to select how many historical conversations you want to keep in memory. This would enable users to have longer conversations before the token limit creates issues. However this feature is not implemented yet..

4. Please leverage encryption mechanism provided by the AWS for services meantioned in architecture.
Here are the links that provide more information about protecting data in the services used.

 Amazon Dynamodb: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-protection.html
 Amazon Cloudfront: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/data-protection-summary.html
 Amazon Lex: https://docs.aws.amazon.com/lexv2/latest/dg/data-protection.html
 Amazon SageMaker: https://docs.aws.amazon.com/sagemaker/latest/dg/data-protection.html
 AWS Lambda: https://docs.aws.amazon.com/lambda/latest/dg/security-dataprotection.html
 Amazon Kendra: https://docs.aws.amazon.com/kendra/latest/dg/data-protection.html

## 4. Prerequisites
You need the following to be installed on your local machine to access the EKS cluster and 

- Premission to create IAM role , DynamoDB,deploy Kendra Lex CloudFront, host files in S3
On the AWS account that you will be deploying this kit you will need an IAM User with -
Administrator and Programmatic access

- Infrastructure to deploy the model: 

- Access to deploy your own API if you choose to go down that route

- Ability to attach Layers to Lambda 

- Git security credentials.

## 5. Quick Start

1. Choose **Launch Stack** and (if prompted) log into your AWS account:

These are the currently supported regions. Click a button to launch it in the desired region.

| Region   |  Launch | CloudFormation Template|
|----------|:-------------:|------------------|
| Northern Virginia | <a target="_blank" href="https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/personalize-solution-staging-us-east-1/kendra-RAG/AmazonKendraRAG.yaml&stackName=conversational-Bot-RAG"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a>     |[us-east-1](https://s3.amazonaws.com/personalize-solution-staging-us-east-1/kendra-RAG/AmazonKendraRAG.yaml)|


2. For **Stack Name**, enter a value unique to your account and region. 
    ![Provide a stack name](assets/pic/StackName.png)  
3. Pick and choose the parameters ,Leave the other parameters as their default values and select **Next**.  
![Pick parameters such as LLM, Kendra Index](assets/pic/CloudformationParameter.png)  
4. Select **I acknowledge that AWS CloudFormation might create IAM resources with custom names**.  
![Provide a stack name](assets/pic/IAgree.png)  
5. Wait 20 minutes for AWS CloudFormation to create the necessary infrastructure stack and module containers.  

Web UI

-----

## 6. Advanced Configuration

### 6.1. Optional CloudFormation Parameters

- Pick and choose the LLM
 
### 5.3. Clean Up

To remove the stack and stop further charges, first select the root stack from the CloudFormation console and then the **Delete** button. This will remove all resources EXCEPT for the S3 bucket containing job data . 

To remove all remaining data, browse to the S3 console and delete the S3 bucket associated with the stack.

-----

## 7. Module Information

### 6.1. LangChain

Please visit [amazon-kendra-langchain-extensions Public
](https://github.com/aws-samples/amazon-kendra-langchain-extensions ) for more information about the JackHMMER algorithm.

(https://python.langchain.com/docs/modules/data_connection/retrievers/integrations/amazon_kendra_retriever)

## 8. FAQ


-----

## 9. Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

-----

## 10. License

This project is licensed under the Apache-2.0 License.
