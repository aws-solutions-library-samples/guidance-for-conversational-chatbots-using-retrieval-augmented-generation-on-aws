# Guidance for Conversational Chatbots using Retrieval Augmented Generation (RAG) on AWS

## Contents

1. [Overview](#1-overview)
2. [Architecture Details](#2-architecture-details)
3. [Disclaimer]
3. [Prerequisites](#3-prerequisites)
4. [Quick Start](#4-quick-start) 
5. [Advanced Configuration](#5-advanced-configuration)  
    5.1. [Optional CloudFormation Parameters](#31-optional-cloudformation-parameters)      
6. [Module Information](#6-module-information)  
    6.1 [LangChain](#61-LangChain)
    6.2 [cloudfront]


7. [FAQ](#6-faq)
8. [Security](#7-security)
9. [License](#8-license)

-----

## 1. Overview

In this implementation we demonstrate how to implement a RAG workflow by combining the capabilities of Amazon Kendra with LLMs to create state-of-the-art GenAI ChatBot providing conversational experiences over your enterprise content. 

To restrict the GenAI application responses to company data only, we need to use a technique called Retrieval Augmented Generation (RAG). An application using the RAG approach retrieves information most relevant to the user’s request from the enterprise knowledge base or content, bundles it as context along with the user’s request as a prompt, and then sends it to the LLM to get a GenAI response. LLMs have limitations around the maximum word count for the input prompt, therefore choosing the right passages among thousands or millions of documents in the enterprise, has a direct impact on the LLM’s accuracy.

Detailed benifits of RAG implementation are published in this popular blog [Quickly build high-accuracy Generative AI applications on enterprise data using Amazon Kendra, LangChain, and large language models](https://aws.amazon.com/blogs/machine-learning/quickly-build-high-accuracy-generative-ai-applications-on-enterprise-data-using-amazon-kendra-langchain-and-large-language-models/), 
and it has some of the code sample too in this [GitHub](https://github.com/aws-samples/amazon-kendra-langchain-extensions/tree/main/kendra_retriever_samples) repository, 

In this particular repository we are goint to provide implementation details to deploy a  serverless chatbot which can scale to sver lauser 
maintain conversational memory 
provide detaisl links
provide variety of orchestrator and also provides multiple ways Lmbda implementation 
simple implementatioa and Advanced Agents implemetaion
1. Query rehrasing or disambiguation
This repository includes the CloudFormation template, Lambda Orchestrators and reference to Chat UI.
2. remember previous conversation
ability to decide whether to call rag or other 

-----

## 2. Architecture Details
![RAG Architecture](assets/pic/RAG_Kendra.png?raw=true "RAG with Amazon Kendra")

The workflow includes the following steps:

1. Financial documents and agreements are stored on Amazon S3, and ingested to an Amazon Kendra index using the S3 data source connector.

2. The LLM is hosted on a SageMaker endpoint.

3. An Amazon Lex chatbot is used to interact with the user via the Amazon Lex web UI.

4. The Amazon DynamoDB is used to hold conversational memory.

5. The solution uses an AWS Lambda function with LangChain to orchestrate between Amazon Kendra, Amazon DynamoDB, Amazon Lex, and the LLM.

6. When users ask the Amazon Lex chatbot for answers from a financial document, Amazon Lex calls the LangChain orchestrator to fulfill the request.

7. Based on the query, the LangChain orchestrator pulls the relevant financial records and paragraphs from Amazon Kendra or pull the information from conversational memory in DynamoDB.

8. The LangChain orchestrator provides these relevant records to the LLM along with the query and relevant prompt to carry out the required activity.

9. The LLM processes the request from the LangChain orchestrator and returns the result.

10. The LangChain orchestrator gets the result from the LLM and sends it to the end-user through the Amazon Lex chatbot.


## 3. Prerequisites
You need the following to be installed on your local machine to access the EKS cluster and 

- Premission to create IAM role , DynamoDB,deploy Kendra Lex CloudFront, host files in S3
On the AWS account that you will be deploying this kit you will need an IAM User with -
Administrator and Programmatic access

- Infrastructure to deploy the model: 
    - [g2],
    - [g24],
    - [g48] for Falcon , 
    - Please raise service request to increase quota
- Access to deploy your own API if you choose to go down that route

- Ability to attach Layers to Lambda 

- Git security credentials.

## 4. Quick Start

1. Choose **Launch Stack** and (if prompted) log into your AWS account:

These are the currently supported regions. Click a button to launch it in the desired region.

| Region   |  Launch | CloudFormation Template|
|----------|:-------------:|------------------|
| Northern Virginia | <a target="_blank" href="https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a>     |[us-east-1](https://aws-bigdata-blog.s3.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|
| Oregon | <a target="_blank" href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog-replica-us-west-2/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog-replica-us-west-2"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |[us-west-2](https://aws-bigdata-blog-replica-us-west-2.s3-us-west-2.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|
| Ireland | <a target="_blank" href="https://eu-west-1.console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog-replica-eu-west-1/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog-replica-eu-west-1"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |[eu-west-1](https://aws-bigdata-blog-replica-eu-west-1.s3-eu-west-1.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|
| Sydney | <a target="_blank" href="https://ap-southeast-2.console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog-replica-ap-southeast-2/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog-replica-ap-southeast-2"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |[ap-southeast-2](https://aws-bigdata-blog-replica-ap-southeast-2.s3-ap-southeast-2.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|
| Singapore | <a target="_blank" href="https://ap-southeast-1.console.aws.amazon.com/cloudformation/home?region=ap-southeast-1#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog-replica-ap-southeast-1a/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog-replica-ap-southeast-1a"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |[ap-southeast-1a](https://aws-bigdata-blog-replica-ap-southeast-1a.s3-ap-southeast-1.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|
| Seoul | <a target="_blank" href="https://ap-northeast-2.console.aws.amazon.com/cloudformation/home?region=ap-northeast-2#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog-replica-ap-northeast-2/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog-replica-ap-northeast-2"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |[ap-northeast-2](https://aws-bigdata-blog-replica-ap-northeast-2.s3-ap-northeast-2.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|
| London | <a target="_blank" href="https://eu-west-2.console.aws.amazon.com/cloudformation/home?region=eu-west-2#/stacks/create/review?templateURL=https://s3.amazonaws.com/aws-bigdata-blog-replica-eu-west-2/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml&stackName=lex-web-ui&param_BootstrapBucket=aws-bigdata-blog-replica-eu-west-2"><span><img height="24px" src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png"/></span></a> |[eu-west-2](https://aws-bigdata-blog-replica-eu-west-2.s3.eu-west-2.amazonaws.com/artifacts/aws-lex-web-ui/artifacts/templates/master.yaml)|

2. For **Stack Name**, enter a value unique to your account and region. 
    ![Provide a stack name](assets/pic/StackName.png)  
3. Pick and choose the parameters ,Leave the other parameters as their default values and select **Next**.  
![Pick parameters such as LLM, Kendra Index](assets/pic/CloudformationParameter.png)  
4. Select **I acknowledge that AWS CloudFormation might create IAM resources with custom names**.  
![Provide a stack name](assets/pic/IAgree.png)  
5. Wait 20 minutes for AWS CloudFormation to create the necessary infrastructure stack and module containers.  

Web UI

-----

## 5. Advanced Configuration

### 5.1. Optional CloudFormation Parameters

- Pick and choos ethe kendra index developer edition and enterprise edition 
- Pick and choose the LLM
 Select "N" for **LaunchSageMakerNotebook** if you do not want to launch a managed sagemaker notebook instance to quickly run the provided Jupyter notebook. This option will avoid the [charges associated with running that notebook instance](https://aws.amazon.com/sagemaker/pricing/).

### 5.3. Clean Up

To remove the stack and stop further charges, first select the root stack from the CloudFormation console and then the **Delete** button. This will remove all resources EXCEPT for the S3 bucket containing job data . 

To remove all remaining data, browse to the S3 console and delete the S3 bucket associated with the stack.

-----

## 6. Module Information

### 6.1. LangChain

Please visit [amazon-kendra-langchain-extensions Public
](https://github.com/aws-samples/amazon-kendra-langchain-extensions ) for more information about the JackHMMER algorithm.

(https://python.langchain.com/docs/modules/data_connection/retrievers/integrations/amazon_kendra_retriever)

## 6. FAQ

Q: When deploying the CloudFormation template, I get an error `Embedded stack arn:aws:cloudformation...  was not successfully created: The following resource(s) failed to create: [AWSServiceRoleForEC2SpotFleetServiceLinkedRole]`. How can I fix this?

This can happen if the service role has already been created in a previous deployment. Try deleting the `AWSServiceRoleForEC2SpotFleetServiceLinkedRole` in the IAM console and redeploy the Cloud Formation template.

-----

## 7. Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

-----

## 8. License

This project is licensed under the Apache-2.0 License.