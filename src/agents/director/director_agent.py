from typing import Tuple
from agents.agent import Agent
import os
from mcp.server.fastmcp import FastMCP
from agents.director.step_manager import StepManager
from decide import safe_make_structured_decision
from env_context_queue import EnvironmentContextQueue
from logger import Logger
from mtypes.contexted_call import ContextedCall, FileLocation
from mtypes.semantic_block import SemanticBlock, SentenceType
from mtypes.goal_steps import GoalStep
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
import agents.professor.professor_agent as professor_agent

from utils.file_interaction import create_file_within_dir, read_relative_file_content,read_file_content, read_json_file_to_dict, write_dict_to_json_file

load_dotenv() 
mcp = FastMCP("director")

class DirectorAgent(Agent):
    def __init__(self, path, context_queue: EnvironmentContextQueue, stepManager: StepManager):
        super().__init__()
        self.logger = Logger()
        self.exit_stack = AsyncExitStack()
        self.stepManager = stepManager
        self.path = path
        self.context_queue = context_queue
        self.goal_file = self.path + "/GOAL.md"
        self.tracker_file = self.path + "/.tutorai/step_tracker.json"
        
        self.messages = []
        


    def start(self):
        goal_base_path = "agents/director/prompts/goal_base.txt"
        goal_base = read_relative_file_content(goal_base_path)

        if not os.path.exists(self.goal_file):
            create_file_within_dir(self.goal_file, goal_base)
        
        if  os.path.exists(self.tracker_file):
            current_step = self.stepManager.get_next_step()
            self.logger.set_group(current_step[2])

    async def update(self):
        if not self.context_queue.is_empty():
            action = self.context_queue.pop_interaction()
            await self.process_interaction(action)
            
    async def process_interaction(self, interaction: SemanticBlock):
        if interaction.origin_file_path == self.goal_file:
            await self.update_plan()
        elif interaction.sentence_type == SentenceType.IMPERATIVE:
            call = ContextedCall(
                topic=interaction.block,
                block_context=interaction.block,
                full_context=interaction.context,
                src_file_path=interaction.origin_file_path,
                target_file_path=interaction.target_file_path)
            await professor_agent.answer_user(call)
            
        elif interaction.sentence_type == SentenceType.INTERROGATIVE:
            await professor_agent.research_topic(interaction.origin_file_path, 
                interaction.context,
                interaction.last_change,
                )
        elif interaction.sentence_type == SentenceType.FINISHED:
            await self.create_next_document(self.path)

        return

    async def update_plan(self):
        prompt_path = ""
        if not os.path.exists(self.tracker_file):
            create_file_within_dir(self.tracker_file)
            prompt_path = f"agents/prompts/director/elaborate_goal.txt"
            old_user_goal = {}
        else:
            prompt_path = f"agents/prompts/director/update_goal.txt"
            old_user_goal = read_file_content(self.tracker_file)

        user_goal = read_file_content(self.goal_file)
        template = read_relative_file_content(prompt_path)
        goal = template.format(user_goal=user_goal, old_user_goal=old_user_goal)
        
        try:
            goal_plan = await safe_make_structured_decision(goal, GoalStep, user_goal)

            plan_dict = goal_plan.model_dump() if hasattr(goal_plan, 'model_dump') else goal_plan.to_dict()

            write_dict_to_json_file(self.tracker_file, plan_dict)

        except Exception as ex:
            print(f"An error occurred while updating the plan: {ex}")

        return

    async def create_next_document(self, file_path):
        next_step = self.stepManager.get_next_step()
        self.logger.set_group(next_step[2])
        await professor_agent.next_step(next_step[0], next_step[1], next_step[2], next_step[3], file_path)
        self.stepManager.complete_next_step()
        
        
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