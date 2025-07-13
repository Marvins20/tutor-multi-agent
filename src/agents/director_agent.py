from typing import Tuple
from agents.agent import Agent
import os
from mcp.server.fastmcp import FastMCP
from env_context_queue import EnvironmentContextQueue
from mtypes.semantic_block import SemanticBlock, SentenceType
from mtypes.goal_steps import GoalStep
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from agents.professor_agent import answer_user, research_topic
import json

load_dotenv() 
mcp = FastMCP("director")

class DirectorAgent(Agent):
    def __init__(self, path, context_queue: EnvironmentContextQueue):
        super().__init__()
        self.path = path
        self.context_queue = context_queue
        self.goal_file = os.path.join(self.path, "GOAL.md")
        self.tracker_file = os.path.join(self.path, ".tutorai/step_tracker.json")
        self.exit_stack = AsyncExitStack()
        self.messages = []

    def start(self):
        if not os.path.exists(self.goal_file):
            os.makedirs(os.path.dirname(self.goal_file), exist_ok=True)
            with open(self.goal_file, 'w') as f:
                f.write("# Project Goal\n\nDefine your project goal here.\n")
        
        if not os.path.exists(self.tracker_file):
            os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)
            with open(self.tracker_file, 'w') as f:
                json.dump({"steps": [], "current_step": 0}, f, indent=2)  

        return      

    async def connect_to_agent_script(self, agent_script_path: str):
        server_params = StdioServerParameters(
            command="python",
            args=[agent_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        return


    async def update(self):
        if not self.context_queue.is_empty():
            action = self.context_queue.pop_interaction()
            await self.process_interaction(action)
            
    async def process_interaction(self, interaction: SemanticBlock):
        if interaction.origin_file_path == self.goal_file:
            await self.update_goal()
        elif interaction.sentence_type == SentenceType.IMPERATIVE:
            await answer_user(interaction.origin_file_path, 
            interaction.location[0], 
            interaction.context, 
            interaction.block)
            
        elif interaction.sentence_type == SentenceType.INTERROGATIVE:
            await research_topic(interaction.origin_file_path, 
                interaction.context,
                interaction.last_change,
                )
        elif interaction.sentence_type == SentenceType.FINISHED:
            await self.create_next_step()

        return

    def update_goal(self):
        if not os.path.exists(self.goal_file):
            raise FileNotFoundError(f"GOAL.md not found at {self.goal_file}")
        
        with open(self.goal_file, 'r') as f:
            goal_content = f.read()

        
        # TODO if a change was made in the goal file, update goal by regenerating tracker file
        # Possible problem: not regenerate steps if the goal file has changed
            # Maybe it can be solved trough the ID
        pass

    def conclude_step_in_tracker(self, step_id:str):
        # TODO traverse json until find ID and set conclude to tru
        pass

    def create_next_step(self):
        next_step = self.get_next_step()
        self.conclude_step_in_tracker(next_step[0])
        #call professor agent to create file structure 


    def get_next_step(self)-> Tuple[int, str, str]:
        pass
