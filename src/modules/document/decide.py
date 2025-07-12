import os
from openai import OpenAI
from dotenv import load_dotenv
from ratelimit import limits, RateLimitException

load_dotenv()

ONE_MINUTE=60

#TODO refine prompt and evalute the possibility to run via lambda function,
# also see how the user could possibly input his specific key or account in order
# to make api calls

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)



@limits(calls=1, period=ONE_MINUTE)
def make_decision(message) -> str:
    system_prompt = (
        "You are a personal Tutor. "
        "Whenever I send you a text "
        "I would like you return me a clear and short text about the subject. "
    )
    response = client.responses.create(
    model="gpt-4o-mini",
    instructions=system_prompt,
    input=message,
    )
    return response.output_text

def safe_make_decision(message) -> str:
    print("chegou aqui")
    try:
        return make_decision(message)
    except RateLimitException:
        print("Rate limit exceeded. Ignoring the call.")
        return ""