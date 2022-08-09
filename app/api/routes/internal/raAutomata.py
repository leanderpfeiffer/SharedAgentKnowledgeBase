from fastapi import APIRouter
from tools.runQuery import runUpdateQuery, runSelectQuery
from tools.createQuery import readQuery, getValue
from decouple import config


baseDIR = config("APIDIR")
queryDIR = baseDIR+"/routes/internal/queries/"

ontoName = config("BASEURI")
router = APIRouter(
    prefix="/ra/getAutomata",
    tags=["Automata"])

getResource = lambda element: getValue(element,"res")

def createRa(capabilities, executions):
    resourceDict = {}
    for element in executions["results"]["bindings"]:
        resource = getValue(element, "resource")
        if resource not in resourceDict:
            resourceDict[resource] = {"capabilities": {}}
            resourceDict[resource]["executions"] = {"proposed": [], "planned": [], "successfull": [], "errored": []}
        resourceDict[resource]["executions"][getValue(element,"status")].append(
                {"specification": getValue(element,"spec"),
                "process": getValue(element,"process"),
                "startTime": getValue(element, "startTime"),
                "endTime": getValue(element, "endTime"),
                }
            )
    for element in capabilities["results"]["bindings"]:
        resource = getResource(element)
        process = element["proc"]["value"].replace(ontoName,"")
        feature = element["feat"]["value"].replace(ontoName,"")
        if resource not in resourceDict.keys():
            resourceDict[resource] = {"capabilities": {}}
        resourceDict[resource]["isActive"] = element["active"]["value"]
         
        
        if feature not in resourceDict[resource]["capabilities"].keys(): 
            resourceDict[resource]["capabilities"][feature] = {"processes": {}}
        resourceDict[resource]["capabilities"][feature]["processes"][process] = {
            "costs": element["cost"]["value"],
            "quality": element["quality"]["value"],
            "emissions": element["emissions"]["value"],
            "duration": element["duration"]["value"]
        }
    return resourceDict


@router.get("/")
def getRaAutomata():
    capabilities = runSelectQuery(readQuery("getCapabilities",queryDIR ))
    executions = runSelectQuery(readQuery("getRAExecutions", queryDIR))
    return createRa(capabilities, executions)