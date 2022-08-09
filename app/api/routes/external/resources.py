from models.raModels import RA_new
from tools.createQuery import createQuery, createQueryFromFile
from tools.runQuery import runUpdateQuery, runSelectQuery
from decouple import config

ontoName = config("BASEURI")
baseDIR = config("APIDIR")
queryDIR = baseDIR+"routes/external/queries"

from fastapi import APIRouter

router = APIRouter(prefix="/resource",tags=["Resource"])

def getValue(element, key):
    return element[key]["value"].strip(ontoName)

#TODO add Checks for queries
@router.post("/activate/{resource}")
def postActivateResource(resource: str):
    query = createQueryFromFile("activateRA",queryDIR, {"resource": resource})
    return runUpdateQuery(query)

@router.post("/deactivate/{resource}")
def postDeactivateResource(resource: str):
    query = createQueryFromFile("deactivateRA", queryDIR, {"resource": resource})
    return runUpdateQuery(query)

@router.post("/add")
def addResource(data: RA_new):
    query = createQueryFromFile("addRA", queryDIR, data.dict())
    return runUpdateQuery(query)

@router.get("/active/{resource}")
def getActive(resource:str):
    query = createQueryFromFile("checkRAactive", queryDIR,{"resource": resource})
    return runSelectQuery(query)["results"]["bindings"][0]["active"]["value"]

@router.get("/performance/{resource}")
def getRAPerformance(resource:str):
    query = createQueryFromFile("getTotalRAPerformance",queryDIR, {"resource": resource})
    performances =  runSelectQuery(query)["results"]["bindings"]
    resultDict = {}
    for element in performances:
        resultDict = {"emissions": element["totalEmissions"]["value"],
                        "quality": element["totalQuality"]["value"],
                        "cost": element["totalCost"]["value"]}
    return resultDict


@router.get("/getCurrentState/{resource}")
def getCurrentState(resource: str):
    query = createQueryFromFile("getCurrentRAState", queryDIR, {"resource": resource})
    currentStateList = runSelectQuery(query)["results"]["bindings"]
    resultDict = {}
    for element in currentStateList:
        resultDict = {
            "execution": getValue(element, "execution"),
            "process": getValue(element, "proc"),
            "specification": getValue(element, "spec")
        }
    return resultDict

@router.get("/getHistory/{resource}")
def getHistory(resource:str):
    query = createQueryFromFile("getRAHistory", queryDIR, {"resource": resource})
    history = runSelectQuery(query)["results"]["bindings"]
    resultDict = {}
    for element in history:
        resultDict.append({
            "execution": getValue(element, "execution"),
            "emissions": getValue(element, "emissions"),
            "costs": getValue(element, "costs"),
            "quality": getValue(element, "quality"),
            "startTime": getValue(element, "startTime"),
            "endTIme": getValue(element, "endTime"),
        })
    return resultDict


@router.get("/getStatus/{resource}")
def getStatus(resource: str):
    
    active = getActive(resource)
    performanceDict = getRAPerformance(resource)
    currentState = getCurrentState(resource)
    history = getHistory(resource)
    return { "active": active, "history": history, "currentState": currentState, "performance": performanceDict}