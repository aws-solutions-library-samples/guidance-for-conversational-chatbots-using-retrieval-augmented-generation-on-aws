#agent
import re
from tools import tools
from langchain.prompts import StringPromptTemplate
from langchain import  LLMChain
from datetime import datetime
from typing import Dict ,List,Union
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
import config

#Each answer from tool has keyword "source" followed by URL,e.g [source:"https://s3.us-east-1.amazonaws.com/bucket/AGREEMENT.PDF"] .Always include source URL for each fact you use in response in this formate example [source:URL] when answer is from tool.
#If you use tool, then always include source URL for each fact you use in response in this format [source:URL].Use only the URL provided in the observations from the tool.NEVER EVER MAKE IT UP.
#If the answer is from conversation history then only include [source : conversation history] in the response, 
# Set up the base template
#template = """You are a conversational AI bot, Answer the following questions based on  conversation history or ONLY by using text from the tool. 
#Answer the following questions based ONLY on search results from the tool or previous conversation history. 
#with ability to email, 
#If Draft email with out using the email tool . USE tool 'email tool' to only send an email 
#answer from the reults of tool and

template = """You are a conversational chatbot named "Financial chatbot". You ONLY ANSWER QUESTIONS ABOUT FINANCE AND AMAZON 2022 10K USING TOOL.
Answer the following QUESTIONs based on search results from the tool.
If a tool is used , then answer the questions using the tool and you should include the source URL at the end of the response in a new line in this format [source:URL] ALWAYS.
If a tool is used and answer from tool is NOT RELAVENT to question ,then respectfully decline the request   ,NEVER make up an answer and DO NOT include source in response.


You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action,usually same search question from Human
Observation: the result of the action
```
When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No

AI: [your response here]

Begin!

Previous conversation history:
{history}

New input: {input}
{agent_scratchpad}"""

class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)

class CustomOutputParser(AgentOutputParser):
    
    ai_prefix: str = "AI"

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if f"{self.ai_prefix}:" in text:
            return AgentFinish(
                {"output": text.split(f"{self.ai_prefix}:")[-1].strip()}, text
            )
        regex = r"Action: (.*?)[\n]*Action Input: ((.|\n)*)"
        match = re.search(regex, text)
        if not match:
            return AgentFinish({"output": text}, text)
        action = match.group(1)
        action_input = match.group(2)
        return AgentAction(action.strip(), action_input.strip(" ").strip('"'), text)

class KendraAgent():
    def __init__(self,llm, memory,tools) -> None:
        self.llm = llm
        self.memory = memory
        self.tools = tools
        self.agent = self.create_agent()

    def create_agent(self):
        
        output_parser = CustomOutputParser()
        tool_names = [tool.name for tool in tools]
        
        prompt= CustomPromptTemplate(
                template=template,
                tools=self.tools,
                input_variables=["input","intermediate_steps","history"]
                )
        
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        
        agent= LLMSingleActionAgent(
                llm_chain=llm_chain,
                output_parser=output_parser,
                stop=["\nObservation:"], 
                allowed_tools=tool_names,
                verbose=True, 
                max_iterations=1
                )
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=self.tools, verbose=True,memory=self.memory)
        return agent_executor

    def run(self, input):
        return self.agent.run(input=input)
