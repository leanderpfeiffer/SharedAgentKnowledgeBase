from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel

class ExecutionProposal(BaseModel):
    resource: str
    process: str
    specification: str
    plannedStartTime: datetime
    plannedEndTime: datetime
    proposalGroup: str


class Performance(BaseModel):
    emissions: float
    quality: Optional[float]
    costs: float

class CompleteExecutionProposalSuccess(BaseModel):
    performance: Performance
    realStartTime: datetime
    realEndTime: datetime

class CompleteExecutionErrored(BaseModel):
    errorMessage: str
    restartOfSpecification: bool
    restartOfProcess: bool