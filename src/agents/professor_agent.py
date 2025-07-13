from logging import log
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv
import os

from decide import safe_make_decision
from document_module.comparator import Comparator
from document_module.document_module import DocumentModule
from document_module.md_manager import MarkdownManager
from document_module.md_parser import MarkdownParser

mcp = FastMCP("professor")
load_dotenv()

ONE_MINUTE=60

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

document_module = DocumentModule(Comparator,MarkdownParser, MarkdownManager)

def _read_prompt(prompt_name):
    """Read prompt template for a specific function"""
    prompt_path = f"prompts/professor/{prompt_name}.txt"

    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"Prompt file not found for {prompt_path}"

def _format_prompt(template, **kwargs):
    """Format prompt template with provided arguments"""
    return template.format(**kwargs)

@mcp.tool()
async def next_step(title, summary, context: str, topic: str):
    """Given a question or order, provide a short and direct answer for the user.
        async def researchTopic(context: str, topic: str, profile: str = "{}"):
    Args:
        context:
        userInput:
        context (str): The context or background information for the research
        topic (str): The topic to research and explain
        profile (str): JSON string containing user's learning profile (optional)
    
    Returns:
        str: Detailed markdown-formatted explanation of the topic
    """
    try:
        prompt_template = _read_prompt("new_step")

        formatted_prompt = _format_prompt(
            prompt_template,
            topic,
            summary,
        )

        answer = safe_make_decision(formatted_prompt)
        
        await document_module.create_document_with_content(file_path, topic, answer)
    except Exception as e:
        log(0, f"**Error**: Unable to process your request. Please try again. ({str(e)})")
        return 


async def answer_user(file_path:str, location:int, context: str, user_input: str):
    """Read prompt template for a specific function
        prompt_path = f"prompts/professor/{function_name}.txt"
        context (str): The context or background information relevant to the question
        user_input (str): The user's question or command
        profile (str): JSON string containing user's learning profile (optional)
    
    Returns:
        str: Brief markdown-formatted answer with context for follow-up functions
    """
    
    
    # Format the prompt with the provided arguments
    
    
    try:
        prompt_template = _read_prompt("answer_user")

        formatted_prompt = _format_prompt(
            prompt_template,
            context=context,
            user_input=user_input
        )
        answer = safe_make_decision(formatted_prompt)

        await document_module.answer_after_in_document(file_path, location, ("#Tutor: "+answer))

    except Exception as e:
        log(0, f"**Error**: Unable to process your request. Please try again. ({str(e)})")
        return 


@mcp.tool()
async def research_topic(file_path: str, context: str, topic: str):
    """Given a question or order, provide a short and direct answer for the user.
        async def researchTopic(context: str, topic: str, profile: str = "{}"):
    Args:
        context:
        userInput:
        context (str): The context or background information for the research
        topic (str): The topic to research and explain
        profile (str): JSON string containing user's learning profile (optional)
    
    Returns:
        str: Detailed markdown-formatted explanation of the topic
    """
    try:
        prompt_template = _read_prompt("research_topic")

        formatted_prompt = _format_prompt(
            prompt_template,
            context=context,
            topic=topic
        )

        answer = safe_make_decision(formatted_prompt)
        
        await document_module.create_document_with_content(file_path, topic, answer)
    except Exception as e:
        log(0, f"**Error**: Unable to process your request. Please try again. ({str(e)})")
        return 


@mcp.tool()
async def elaborate_question(file_path: str, context: str = ""):
    """Given a title for a topic, provide a detailed explanation or summary of the subject.

    Args:
        subject (str): The subject area for which to create questions or tasks
        profile (str): JSON string containing user's learning profile and capabilities
        context (str): Additional context information (optional)
    
    Returns:
        str: Markdown-formatted list of questions or project steps tailored to user's profile
    """
    # Read the prompt template
    try:
        prompt_template = _read_prompt("elaborate_question")

        formatted_prompt = _format_prompt(
            prompt_template,
            context=context,
        )

        answer = safe_make_decision(formatted_prompt)
        
        await document_module.create_document_with_content(file_path, answer)
    except Exception as e:
        return f"**Error**: Unable to elaborate questions. Please try again. ({str(e)})"

@mcp.tool()
async def profile_user_progress(user_response: str, context: str = "", current_profile: str = "{}"):
    """Extract and analyze user's learning profile and progress from their response.
    Args:
        subject: str
        user_response (str): The user's response to analyze for proficiency and learning preferences
        context (str): Context about the interaction or subject matter (optional)
        current_profile (str): JSON string of existing user profile to update (optional)
    returns
        str: JSON string containing updated user profile and markdown summary with recommendations
    """
    # Read the prompt template
    prompt_template = read_prompt("profile_user_progress")
    
    # Format the prompt with the provided arguments
    formatted_prompt = format_prompt(
        prompt_template,
        user_response=user_response,
        context=context,
        current_profile=current_profile
    )
    # Initialize OpenAI client
    client = OpenAI()
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": formatted_prompt}
            ],
            temperature=0.6
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"**Error**: Unable to profile user progress. Please try again. ({str(e)})"


async def evaluate_answer(context: str, question_block: str, user_answer: str, profile: str = "{}"):
    """
    Note:
        This function requires:

        context (str): The context or subject matter of the question
        question_block (str): The original question or task that was given to the user
        user_answer (str): The user's response to evaluate
        profile (str): JSON string containing user's learning profile (optional)
    
    Returns:
        str: Markdown-formatted evaluation with feedback, score, and updated profile insights
    """
    # Read the prompt template
    prompt_template = read_prompt("evaluate_answer")
    
    # Format the prompt with the provided arguments
    formatted_prompt = format_prompt(
        prompt_template,
        context=context,
        question_block=question_block,
        user_answer=user_answer,
        profile=profile
    )
    
    # Initialize OpenAI client
    client = OpenAI()
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": formatted_prompt}
            ],
            temperature=0.6
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"**Error**: Unable to evaluate answer. Please try again. ({str(e)})"