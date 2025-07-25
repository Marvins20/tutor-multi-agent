from pydantic import BaseModel

class GoalStep(BaseModel):
    title: str
    summary: str
    done: bool = False
    subtopics: list['GoalStep']