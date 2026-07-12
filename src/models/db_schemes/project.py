from typing import Optional

from pydantic import BaseModel, Field , validator
from bson.objectid import ObjectId

class Project_schema(BaseModel):
    _id  : Optional[ObjectId] 
    project_id : str = Field(...,min_length = 1 )

    # validate project_id to be num or letter  
    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    class Config:
        arbitrary_types_allowed = True
    
