from fastapi import APIRouter, Response
from models.paModels import PA_Data
from tools.createQuery import createQueryFromFile, readQuery, createQuery
from tools.runQuery import runUpdateQuery, runSelectQuery
from decouple import config

baseDIR = config("APIDIR")
queryDIR = baseDIR + "routes/external/queries"
ontoName = config("BASEURI")

router = APIRouter(prefix="/spec",tags=["Specification"])


def getValue(element, key):
    return element[key]["value"].strip(ontoName)


#TODO add Checks for queries
@router.post("/add")
def postAddPA(data: PA_Data):
    query = createQueryFromFile("addPA",queryDIR , data.dict())
    return runUpdateQuery(query)
    #TODO Check if consistent !!

@router.get("/")
def getPA():
    return [getValue(x,"spec") for x in runSelectQuery(readQuery("getPAs", queryDIR))["results"]["bindings"]]

@router.get("/performance/{spec}")
def getPAPerformance(spec:str):
    query = createQueryFromFile("getTotalPAPerformance",queryDIR, {"spec": spec})
    performance = runSelectQuery(query)["results"]["bindings"][0]
    return {"emissions": performance["totalEmissions"]["value"],
                        "quality": performance["totalQuality"]["value"],
                        "cost": performance["totalCost"]["value"]}
    
@router.get("/featureState/{spec}")
def getFeatureState(spec: str):
    query = createQueryFromFile("getPAFeatures",queryDIR, {"spec":spec})
    featureStateList =  runSelectQuery(query)["results"]["bindings"]
    return [{"feature": x["feature"]["value"], "status": x["status"]["value"]} for x in featureStateList]

@router.get("/getHistory/{spec}")
def getHistory(spec: str):
    query =  createQueryFromFile("getPAHistory",queryDIR, {"spec": spec})
    history = runSelectQuery(query)["results"]["bindings"]
    prodHistory = []
    for element in history:
        newDict = {}
        for key in element:
            newDict[key] = element[key]["value"].replace(ontoName,"")
        prodHistory.append(newDict)
    return prodHistory

@router.get("/getCurrentState/{spec}")
def getCurrentState(spec: str):
    query = createQueryFromFile("getCurrentPAState", queryDIR, {"spec": spec})
    currentStateList = runSelectQuery(query)["results"]["bindings"]
    resultDict = {}
    for element in currentStateList:
        resultDict[getValue(element, "pe")] = {
            "resource": getValue(element, "resource"),
            "process": getValue(element, "process"),
        }
    return resultDict

#TODO check for completed spec
@router.get("/getStatus/{spec}")
def getStatus(spec: str):
    performance = getPAPerformance(spec)
    currentState = getCurrentState(spec)
    history = getHistory(spec)
    
    return {"currentState": currentState, "history": history, "performance": performance}


@router.post("/{spec}/deleteFeature/{feat}")
def postDeleteFeature(spec: str, feat:str, response: Response):
    dataDict = {"feat": feat, "spec": spec}
    deleteAllowed = createQueryFromFile("checkDeletePAFeature",queryDIR, dataDict)
    errors = runSelectQuery(deleteAllowed)
    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] for x in errors["results"]["bindings"]]
    deleteQuery = createQueryFromFile("deletePAFeature", queryDIR , dataDict)
    return runUpdateQuery(deleteQuery)

@router.post("/{spec}/addFeature/{feat}")
def postAddFeature(spec: str, feat:str, response: Response):
    dataDict = {"feat": feat, "spec": spec}
    addAllowed = createQueryFromFile("checkAddPAFeature", queryDIR, dataDict)
    print(addAllowed)
    errors = runSelectQuery(addAllowed)
    if len(errors["results"]["bindings"]) != 0:
        response.status_code = 403
        return [x["error"]["value"] for x in errors["results"]["bindings"]]
    addQuery = createQueryFromFile("addPAFeature", queryDIR ,dataDict)
    #*  OPTIONAL: Check if spec has already been completed
    return runUpdateQuery(addQuery)
