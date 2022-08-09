from models.executionModels import ExecutionProposal, CompleteExecutionErrored, CompleteExecutionProposalSuccess
from tools.createQuery import createQueryFromFile
from tools.runQuery import runUpdateQuery, runSelectQuery

from fastapi import APIRouter, Response
from decouple import config
from uuid import uuid4

baseDIR = config("APIDIR")
queryDIR = baseDIR+"/routes/internal/queries/"

router = APIRouter(
    prefix="/processExecutions",
    tags=["processExecutions"])


@router.post("/addProposal")
def postAddProposal(data: ExecutionProposal, response: Response):
    queryCheck = createQueryFromFile("checkProposal", queryDIR, data.dict())
    errors = runSelectQuery(queryCheck)

    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] for x in errors["results"]["bindings"]]
    
    peID = str(uuid4())
    queryAdd = createQueryFromFile("addProposal",queryDIR, {"data": data.dict(), "PEID": peID})
    runUpdateQuery(queryAdd)
    return {"processExecutionId": peID}
    
@router.post("/selectProposal/{processExecutionId}")
def postSelectProposal(processExecutionId: str, response: Response):
    queryCheck = createQueryFromFile("checkIfProposalSelectable", queryDIR,  {"processExecution": processExecutionId})
    errors = runSelectQuery(queryCheck)

    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] + " ("+x["criticalPart"]["value"]+ ")" for x in errors["results"]["bindings"]]
    
    querySelect =  createQueryFromFile("selectProposal", queryDIR, {"processExecution": processExecutionId})
    return runUpdateQuery(querySelect) 


@router.post("/executionRunning/{processExecutionId}")
def postExecutionRunning(processExecutionId: str, response:Response):
    queryCheck =  createQueryFromFile("checkExecutionRunnable", queryDIR, {"processExecution": processExecutionId})
    errors = runSelectQuery(queryCheck)

    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] for x in errors["results"]["bindings"]]
    
    queryRun =  createQueryFromFile("setExecutionRunning", queryDIR, {"processExecution": processExecutionId})
    return runUpdateQuery(queryRun)


@router.post("/executionSuccessfull/{processExecutionId}")
def postExecutionSuccessfull(processExecutionId: str,data: CompleteExecutionProposalSuccess,  response: Response):
    queryCheck = createQueryFromFile("checkExecutionCompletable", queryDIR, {"processExecution": processExecutionId})
    errors = runSelectQuery(queryCheck)

    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] for x in errors["results"]["bindings"]]
    
    queryComplete = createQueryFromFile("setExecutionSuccessfull", queryDIR, {"data": data.dict(), "processExecution": processExecutionId})
    print(queryComplete)
    return runUpdateQuery(queryComplete) 

@router.post("/executionErrored/{processExecutionId}")
def postExecutionErrored(processExecutionId: str, data:  CompleteExecutionErrored,  response: Response):
    queryCheck = createQueryFromFile("checkExecutionCompletable", queryDIR, {"processExecution": processExecutionId})
    errors = runSelectQuery(queryCheck)

    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] for x in errors["results"]["bindings"]]
    
    
    queryComplete = createQueryFromFile("setExecutionErrored", queryDIR, {"data": data.dict(), "processExecution": processExecutionId})
    runUpdateQuery(queryComplete) 
    if data.restartOfSpecification:
        return "Restart of Specification Triggered" #TODO
    elif data.restartOfProcess:
        return "Restart of Process Triggered" #TODO 
    else:
        return "Error Noted"