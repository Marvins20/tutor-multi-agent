from pydantic import BaseModel

class GoalStep(BaseModel):
    step_id: int
    title: str
    description: str
    is_completed: bool = False
    substeps: list['GoalStep'] = []