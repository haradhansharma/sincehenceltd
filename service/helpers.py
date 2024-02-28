import json
from django.db import models

def get_project_created(obj):
    
    if obj.previous_todo is not None and obj.previous_todo.target_date is not None:
        project_created = obj.previous_todo.target_date
    else:
        project_created = obj.project.created_at    
        
    return  project_created

