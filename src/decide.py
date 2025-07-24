import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from ratelimit import limits, RateLimitException
import json

from logger import Logger

ONE_MINUTE=60

load_dotenv()


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

logger = Logger("")


@limits(calls=1, period=ONE_MINUTE)
async def _make_decision(message, model, temperature) -> str:
    try:
        response =  client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": message}
            ],
            temperature=temperature
        )
        
        answer = response.choices[0].message.content
        
        return answer
    except Exception as e:
        print(0, f"**Error**: Unable to process your request. Please try again. ({str(e)})")
        return ""

async def safe_make_decision(message,noprompt, model="gpt-4", temperature=0.7) -> str:
    try:
        start_time = time.time()
        decision = await _make_decision(message, model, temperature)
        end_time = time.time()
        duration = end_time - start_time
        logger.log_token_and_time_usage(message, noprompt, duration)
        return decision 
    except RateLimitException:
        print("Rate limit exceeded. Ignoring the call.")
        return ""
    
    except Exception as e:
        print(f"An error occurred: {e}")

@limits(calls=1, period=ONE_MINUTE)
async def _make_structured_decision(message, structure_model, model, temperature) -> str:
    
    
    try:

        response = client.responses.parse(
            model=model,
            temperature=temperature,
            input=[
                {"role": "system", "content": message},
            ],
            text_format=structure_model,
        )
        

        return response.output_parsed
    except Exception as e:
        print(0, f"**Error**: Unable to process your request. Please try again. ({str(e)})")
        return ""


async def safe_make_structured_decision(message, structure_model, noprompt, model="gpt-4o-2024-08-06", temperature=0.3) -> str:
    try:
        start_time = time.time()
        decision = await _make_structured_decision(message,structure_model, model, temperature)
        end_time = time.time()
        duration = end_time - start_time
        logger.log_token_and_time_usage(message, noprompt, duration)
        return decision

    except RateLimitException:
        print("Rate limit exceeded. Ignoring the call.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")



# async def main():
#     prompt_path = f"/Users/marcusabr/Dev/introduction-ai/tutor-agent/src/agents/prompts/director/elaborate_goal.txt"
#     message = ""
#     with open("/Users/marcusabr/Dev/introduction-ai/tutor-agent/src/agents/prompts/director/goal_base.txt", 'r', encoding='utf-8') as file:
#         message = file.read()
#     answer = await safe_make_structured_decision(message, GoalStep, prompt_path)


# if __name__ == "__main__":
#     import asyncio
    # asyncio.run(main())

# response = client.responses.create(
    # model="gpt-4o-mini",
    # instructions=system_prompt,
    # input=message,
    # )
    # return response.output_text