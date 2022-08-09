from fastapi import APIRouter
from tools.runQuery import runUpdateQuery, runSelectQuery
from tools.createQuery import readQuery, getValue
from optimization.MILP.main import runMILP
from routes.internal.raAutomata import getRaAutomata
from decouple import config
from decouple import config

baseDIR = config("APIDIR")
queryDIR =  "./routes/internal/queries/"

ontoName = config("BASEURI")
router = APIRouter(
    prefix="/pa/getAutomata",
    tags=["Automata"])

getProduct = lambda element: getValue(element,"spec")
getFeature = lambda element, featureNumber=None: getValue(element, "feat" + str(featureNumber) if featureNumber else "feat")

def implementStates(states, productDict={}):
    for element in states["results"]["bindings"]:
        product = getProduct(element)
        feature = getFeature(element)
        if product not in productDict.keys():
            productDict[product] = {
                "globalDealine": element["deadline"]["value"],
                "currentPosition": None,
                "states": {},
                "transitions": {},
                "objectiveFunction": {}}
        productDict[product]["states"][feature] = {
            "desiredPhysicalProperty": feature,
            "scheduling": getValue(element,"status") if "status" in element.keys() else "none",
            "guards": {
                "localDeadlineConstraint": None,
                "customerDeadlineConstraint": None,
                "qualityConstraint": None
            },
            "initialState": (feature == "start"),
            "finalState": (feature == "end")
        }
        if "status" in element.keys():
            productDict[product]["states"][feature]["schedule"] = {
                "resource": getValue(element, "res"),
                "process": getValue(element, "process"),
                "startTime": getValue(element, "startTime"),
                "endTime": getValue(element, "endTime"),
                
            }
    return productDict

def implementObjectiveFunction(objectiveFunction, productDict):
    for element in objectiveFunction["results"]["bindings"]:
        product = getProduct(element)
        productDict[product]["priority"] = element["priority"]["value"]
        if "objectiveFunction" not in productDict[product].keys():
            productDict[product]["objectiveFunction"] = {}
        productDict[product]["objectiveFunction"][getValue(element, "type")] = getValue(element, "value")
    return productDict


def implementTransitions(transitions, productDict):
    for element in transitions["results"]["bindings"]:
        product = getProduct(element)
        feature1 = getFeature(element, 1)
        feature2 = getFeature(element, 2)
        resource = element["res"]["value"].replace(ontoName, "")
        process = element["proc"]["value"].replace(ontoName, "")
        transitionName = "run"+feature1+feature2
        if transitionName not in productDict[product]["transitions"].keys():
            productDict[product]["transitions"][transitionName] = {
                "parent": feature1,
                "child": feature2,
                "programCall": {
                },
                "invariants": {
                    "localDeadlineConstraint": None,
                    "customerDeadlineConstraint": None,
                    "qualityConstraint": None
                },
                "resets": {
                    "powerUsage": None
                }
            }
        if process not in productDict[product]["transitions"][transitionName]["programCall"].keys():
            productDict[product]["transitions"][transitionName]["programCall"][process] = {
                "possibleResources": []}
        productDict[product]["transitions"][transitionName]["programCall"][process]["possibleResources"].append(
            resource)
    return productDict


# TODO include current state

@router.get("/")
def getPaAutomata():
    states = runSelectQuery(readQuery("getPAStates", queryDIR))
    objectiveFunction = runSelectQuery(readQuery("getObjectiveFunction", queryDIR))
    transitions = runSelectQuery(readQuery("getPATransitions", queryDIR))
    productDict = implementStates(states)
    productDict = implementObjectiveFunction(objectiveFunction, productDict)
    productDict = implementTransitions(transitions, productDict)

    return productDict

@router.get("/withRecommendation/")
def getExtendedPaAutomata():
    return runMILP(getPaAutomata(), getRaAutomata())
    