from datetime import datetime
from typing import List
from pydantic import BaseModel

class ObjectiveFunction(BaseModel):
    timeCoeff: float
    costCoeff: float
    emissionCoeff: float
    qualityCoeff: float

class PA_Data(BaseModel):
    id: str
    specification: str
    deadline: datetime
    features: List[str] = []
    objectiveFunction: ObjectiveFunction
    priority: float


