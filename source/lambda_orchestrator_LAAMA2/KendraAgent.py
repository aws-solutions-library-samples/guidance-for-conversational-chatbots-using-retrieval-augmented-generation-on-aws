#agent

import re
from tools import tools
from langchain.prompts import StringPromptTemplate
from langchain import  LLMChain
from datetime import datetime
from typing import Dict ,List,Union
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.schema import AgentAction, AgentFinish


#Template for LLAMA2
template = """You are a conversational AI bot, Answer the questions as best you can using results from the search tool.
You have access to the following tools:

{tools}

To use a tool, STRICTLY follow below format:

```
Thought: Do I need to use a tool? YES
Action: the action to take, should be one of [{tool_names}]
Action Input: the search key words ONLY
Observation: the result of the search
```
YOU MUST USE THE BELOW FORMAT ,if you have a response to say to the user, or if you do not need to use a tool,

```
Thought: Do I need to use a tool? NO
AI: [your response here]


Example 1 Start:
Question: What is the  population of India?
Thought: Do I need to use a tool? YES
Action: Search
Action Input: population of India
Observation:  India is in Asia.The current estimated population of India is approximately 1.38 billion. Its capital is D
Thought: Do I need to use a tool again ? NO
AI: The population of India is approximately 1.38 billion based on the search results
Example 1 End

Example 2 Start:
Question: How are you?
Thought: Do I need to use a tool? NO
AI: I'm doing good. How are you?
Example 2 End

YOU MUST ALWAYS USE PREFIX "AI:" TO RESPOND TO USER with FINAL ANSWER.

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
