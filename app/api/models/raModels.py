
from typing import List
from pydantic import BaseModel

class RA_new(BaseModel):
    name: str
    resourceType: str
    neighbours: List[str]
    capabilities: List[str]
    isActive: bool
    