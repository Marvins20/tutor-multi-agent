import os
from typing import Optional, Tuple
from mtypes.goal_steps import GoalStep
from utils.file_interaction import read_file_content, read_json_file_to_dict, write_dict_to_json_file


class StepManager:
    def __init__(self, path):
        self.tracker_file = os.path.join(path, ".tutorai/step_tracker.json")

    def get_next_step(self):
        step_current = 0

        def dfs_find_first_incomplete(step: GoalStep, step_number:int, step_context) -> Tuple[str, str] | None:
            nonlocal step_current 
            step_current +=1

            step_context += [str(step_current)+" "+step.title]
            if not step.done:
                return step.title, step.summary, step_current, step_context

            for idx,subtopic in enumerate(step.subtopics, 1):
                result = dfs_find_first_incomplete(subtopic, step_number+idx, step_context)
                if result:
                    return result
            
            return None
            
        try:
            goal_tree_dict = read_json_file_to_dict(self.tracker_file)
            if not goal_tree_dict:
                return None, "Tracker file is empty", "Please create a goal first"
            goal_tree_model = GoalStep.model_validate(goal_tree_dict)
            
        except FileNotFoundError:
            return None, "No goal tracker file found", "Please create a goal first"
        except Exception as ex:
            return None, f"Error reading tracker file: {ex}", "Please check the tracker file format"    
        

        result = dfs_find_first_incomplete(goal_tree_model, 0, [])
        print(result)
        if result:
            return result
        
    def complete_next_step(self):
        def dfs_mark_first_incomplete(step: GoalStep) -> GoalStep:
            updated = False
            def _traverse_and_update(current_step: GoalStep):
                nonlocal updated
                if updated:
                    return

                if not current_step.done:
                    current_step.done = True
                    updated = True
                    return
                
                for subtopic in current_step.subtopics:
                    _traverse_and_update(subtopic)

            _traverse_and_update(step)
            return step 

        try:
            goal_tree = read_json_file_to_dict(self.tracker_file)
            goal_tree_model = GoalStep.model_validate(goal_tree)
            new_goal_tree = dfs_mark_first_incomplete(goal_tree_model)
            plan_dict = new_goal_tree.model_dump() if hasattr(new_goal_tree, 'model_dump') else new_goal_tree.to_dict()
            write_dict_to_json_file(self.tracker_file, plan_dict)
        except FileNotFoundError:
            return None, "No goal tracker file found", "Please create a goal first"
        except Exception as ex:
            return None, f"Error reading tracker file: {ex}", "Please check the tracker file format"            
        