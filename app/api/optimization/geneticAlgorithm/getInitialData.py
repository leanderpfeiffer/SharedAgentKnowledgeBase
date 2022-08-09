
import json
from random import randrange
from routes.internal.paAutomata import getPaAutomata
from routes.internal.raAutomata import getRaAutomata

from copy import deepcopy

def getSpecifiedState(states: dict, stateType: str):
    for state in states.keys():
        if states[state][stateType]:
            return state

def convertDictValuesToFloat(originalDict):
    newDict = {}
    for key in originalDict:
        newDict[key] = float(originalDict[key])
    return newDict

def buildFeatureChain(base: dict, originalFeatureChains: list, iteration: int):
    if iteration < base["stateCount"]:
        possibleFeatureChains = []
        for featureChain in originalFeatureChains:
            lastState = featureChain[-1]
            for transition in base["transitions"].values():
                if transition["parent"] == lastState:
                    possibleFeatureChains.append(
                        [*featureChain, transition["child"]])
        return buildFeatureChain(base, possibleFeatureChains, iteration + 1)
    else:
        vaildFeatureChains = []
        for featureChain in originalFeatureChains:
            cleanedFeatureChain = list(dict.fromkeys(featureChain))
            if featureChain[0] == base["startState"] and featureChain[-1] == base["endState"] and len(cleanedFeatureChain) == base["stateCount"]:
                vaildFeatureChains.append(featureChain)
        return vaildFeatureChains


def createBaseChromosome():
    paAutomata = getPaAutomata()
    baseChromosome = {}
    for spec in paAutomata.keys():
        base = {
            "stateCount": len(paAutomata[spec]["states"].keys()),
            "transitions": paAutomata[spec]["transitions"],
            "startState": getSpecifiedState(paAutomata[spec]["states"], "initialState"),
            "endState": getSpecifiedState(paAutomata[spec]["states"], "finalState")
        }
        baseChromosome[spec] = {"priority": float(paAutomata[spec]["priority"]),
                                "objectiveFunction": convertDictValuesToFloat(paAutomata[spec]["objectiveFunction"]),
                                "possibleFeatureChains": buildFeatureChain(base, [[base["startState"]]], 1)}
    return baseChromosome


def getFeatureResourceMapping():
    raAutomata = getRaAutomata()
    featureResourceMapping = {}
    for resource in raAutomata.keys():
        if raAutomata[resource]["isActive"]:
            for feature in raAutomata[resource]["capabilities"]:
                if feature not in featureResourceMapping.keys():
                    featureResourceMapping[feature] = []
                for process in raAutomata[resource]["capabilities"][feature]["processes"]:
                    expectedPerformance = raAutomata[resource]["capabilities"][feature]["processes"][process]
                    featureResourceMapping[feature].append({
                        "feature": feature,
                        "resource": resource,
                        "process": process,
                        "expectedPerformance": convertDictValuesToFloat(expectedPerformance)}
                    )
    return featureResourceMapping



def createInitialGenome(genomeSize: int, featureResourceMapping: dict):
    baseChromosome = createBaseChromosome()
    
    initialGenome = [deepcopy(baseChromosome) for _ in range(genomeSize)]
    for chromosome in initialGenome:

        for spec in chromosome:
            possibleFeatureChains = chromosome[spec]["possibleFeatureChains"]
            
            selectedFeatureChainIndex = randrange(0, len(possibleFeatureChains)) 
            selectedFeatureChain = possibleFeatureChains[selectedFeatureChainIndex]

            selectedResourceChain = []
            for feature in selectedFeatureChain:
                possibleResources = featureResourceMapping[feature]
                selectedResourceIndex = randrange(0, len(possibleResources))
                selectedResourceChain.append(possibleResources[selectedResourceIndex])

            chromosome[spec]["resourceChain"] = selectedResourceChain
        
    return initialGenome