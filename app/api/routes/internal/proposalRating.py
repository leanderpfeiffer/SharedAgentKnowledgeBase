from tools.createQuery import createQueryFromFile, getValue
from tools.runQuery import runUpdateQuery, runSelectQuery, runAskQuery

from datetime import datetime
from fastapi import APIRouter, Response
from decouple import config

baseDIR = config("APIDIR")
queryDIR = baseDIR+"routes/internal/queries/"

router = APIRouter(
    prefix="/proposalRating",
    tags=["proposalRating"])


@router.get("/objectiveFunctions/{proposalGroup}")
def getObjectiveFunctions(proposalGroup: str, response: Response):
    checkQuery = createQueryFromFile("checkProposalGroupExists", queryDIR, {"proposalGroup": proposalGroup})

    if not runAskQuery(checkQuery, reasoningBool=True):
        response.status_code = 403
        return "ProposalGroup not found"

    getQuery = createQueryFromFile("getProposalGroupObjectiveFunctions", queryDIR, {
                                   "proposalGroup": proposalGroup})
    functions = runSelectQuery(getQuery)["results"]["bindings"]
    returnDict = {}
    for element in functions:
        spec = getValue(element, "spec")
        if spec not in returnDict.keys():
            returnDict[spec] = {"priority": float(getValue(element, "priority"))}
        returnDict[spec][getValue(element,"type")] = float(getValue(element,"value"))
    return returnDict


@router.get("/performance/{proposalGroup}")
def getPerformance(proposalGroup: str, response: Response):
    checkQuery = createQueryFromFile("checkProposalGroupExists", queryDIR, {
                                     "proposalGroup": proposalGroup})

    if not runAskQuery(checkQuery, reasoningBool=True):
        response.status_code = 403
        return "ProposalGroup not found"

    getQuery = createQueryFromFile("getProposalPerformance", queryDIR, {
                                   "proposalGroup": proposalGroup})

    performances = runSelectQuery(getQuery)["results"]["bindings"]
    returnDict = {}
    for performance in performances:
        specName = getValue(performance, "spec")
        if specName not in returnDict.keys():
            returnDict[specName] = []

        startTime = datetime.fromisoformat(getValue(performance, "startTime"))
        endTime = datetime.fromisoformat(getValue(performance, "endTime"))
        returnDict[getValue(performance, "spec")].append({
            "type": getValue(performance, "type"),
            "emissions": float(getValue(performance, "emissions")),
            "quality": float(getValue(performance, "quality")),
            "costs": float(getValue(performance, "costs")),
            "duration": (endTime - startTime).total_seconds()
        })
    return returnDict


@router.get("/evaluation/{proposalGroup}")
def getEvaluation(proposalGroup: str, response: Response):
    objectiveFunctions = getObjectiveFunctions(proposalGroup=proposalGroup, response=response)
    perfomances = getPerformance(proposalGroup=proposalGroup, response=response)

    if response.status_code == 403:
        return {"objectiveFunction": objectiveFunctions, "performances": perfomances}
    totalValue = 0

    for spec in perfomances:
        priority = objectiveFunctions[spec]["priority"]
        objectiveFunction = objectiveFunctions[spec]
        for performance in perfomances[spec]:
            helpSum = 0
            for key in performance.keys():
                if key in objectiveFunction.keys():
                    helpSum += performance[key] * objectiveFunction[key]
            totalValue += 1/priority * helpSum
            # TODO normalize and optimize
    return {"totalEvaluation": totalValue}
