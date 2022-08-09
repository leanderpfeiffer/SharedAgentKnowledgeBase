import uuid
import pulp
from datetime import datetime


inf = 10000000000


def convertToTimeStamp(date: str):
    return datetime.fromisoformat(date).timestamp() - int(datetime.now().timestamp()/100000) * 100000


def convertToISOFormat(t: float):
    return datetime.fromtimestamp(round(t + int(datetime.now().timestamp()/100000) * 100000)).isoformat()


def runMILP(paAutomata, raAutomata):
    now = datetime.now().timestamp() - int(datetime.now().timestamp()/100000) * 100000

    # * get Specification Array
    specList = list(paAutomata.keys())

    # * get Resource Arrays
    resList = [res for res in raAutomata if raAutomata[res]["isActive"]]

    # * restructure data from autamata to make it more accessible
    specResFeatMapping = {}
    for spec in specList:

        specResFeatMapping[spec] = {"features": {},
                                    "priority": float(paAutomata[spec]["priority"]),
                                    "timeCoeff": float(paAutomata[spec]["objectiveFunction"]["duration"]),
                                    "transitions": [],
                                    "history": {}}

        for state in paAutomata[spec]["states"]:
            possibleResources = [
                key for key in raAutomata if state in raAutomata[key]["capabilities"].keys()]
            resourceDict = {}
            for resource in possibleResources:
                processes = raAutomata[resource]["capabilities"][state]["processes"]
                maxProcess = list(processes.keys())[0]
                for process in processes:
                    maxProcess = process if float(processes[process]["costs"]) < float(
                        processes[maxProcess]["costs"]) else maxProcess
                # TODO add option of weighing costs according to order
                resourceDict[resource] = {
                    "process": maxProcess,
                    "costs": float(processes[maxProcess]["costs"]),
                    "duration": float(processes[maxProcess]["duration"])}
            specResFeatMapping[spec]["features"][state] = resourceDict
            if paAutomata[spec]["states"][state]["scheduling"] != "none":
                specResFeatMapping[spec]["history"][state] = paAutomata[spec]["states"][state]["schedule"]
            else:
                specResFeatMapping[spec]["history"][state] = {"resource": None}

        for transition in paAutomata[spec]["transitions"]:
            specResFeatMapping[spec]["transitions"].append(
                (paAutomata[spec]["transitions"][transition]["parent"], paAutomata[spec]["transitions"][transition]["child"]))

    specFeatureMapping = [
        (spec, feature) for spec in specResFeatMapping for feature in specResFeatMapping[spec]["features"]]

    featureCombinations = [(spec, *combination) for spec in specList for combination in pulp.allcombinations(list(
        specResFeatMapping[spec]["features"].keys()), 2) if len(combination) == 2 and combination[0] != combination[1]]

    bDict = pulp.LpVariable.dicts("b", featureCombinations, cat=pulp.LpBinary)

    # * create a bunch of timeslots (#features per spec which are relevant for resource)
    slotMapping = {resource: [str(uuid.uuid4()) for spec in specResFeatMapping for feature in specResFeatMapping[spec]
                              ["features"] if resource in specResFeatMapping[spec]["features"][feature].keys()] for resource in resList}

    slotCompinations = [(res, *slots) for res in slotMapping for slots in pulp.allcombinations(
        slotMapping[res], 2) if len(slots) == 2]

    cDict = pulp.LpVariable.dicts("c", slotCompinations, cat=pulp.LpBinary)
    resSlotMapping = [(res, slot)
                      for res in slotMapping for slot in slotMapping[res]]

    # * create a start and endTime ("Ts1","RA1","t1") and ("Te1", "RA1","t1") for each timeslot and resource / all > 0
    tsRT = [("Ts_RT", *combRT) for combRT in resSlotMapping]
    teRT = [("Te_RT", *combRT) for combRT in resSlotMapping]
    tsRTDict = pulp.LpVariable.dicts("Ts_RT", tsRT, lowBound=now)
    teRTDict = pulp.LpVariable.dicts("Te_RT", teRT, lowBound=now)

    # * create a start and endTime ("Ts2","PA1","feat1") and ("Te2", "PA1","feat1") for each feature of a specification / all > 0
    tsSF = [("Ts_SF", *combSF) for combSF in specFeatureMapping]
    teSF = [("Te_SF", *combSF) for combSF in specFeatureMapping]
    tsSFDict = pulp.LpVariable.dicts("Ts_SF", tsSF, lowBound=now)
    teSFDict = pulp.LpVariable.dicts("Te_SF", teSF, lowBound=now)

    # * create a binary variable ("W","PA1","feat1","RA1","t1") that assigns everything together and set impossible combinations to 0
    w = [("W", *combSF, *combRT)
         for combSF in specFeatureMapping for combRT in resSlotMapping]
    wDict = pulp.LpVariable.dicts("W", w, cat=pulp.LpBinary)
    for element in w:  # element = ("W", spec, feat, res, slot)
        if element[3] not in specResFeatMapping[element[1]]["features"][element[2]]:
            wDict[element].setInitialValue(0)
            wDict[element].fixValue()

    preScheduledExecutions = []
    for combSF in specFeatureMapping:
        if specResFeatMapping[combSF[0]]["history"][combSF[1]]["resource"]:
            resource = specResFeatMapping[combSF[0]
                                          ]["history"][combSF[1]]["resource"]
            slotIndex = 0
            slots = slotMapping[resource]
            while wDict[("W", *combSF, resource, slots[slotIndex])].value() == 1:
                slotIndex += 1

            slot = slots[slotIndex]
            wDict[("W", *combSF, resource, slot)].setInitialValue(1)
            wDict[("W", *combSF, resource, slot)].fixValue()
            startTime = specResFeatMapping[combSF[0]
                                           ]["history"][combSF[1]]["startTime"]
            endTime = specResFeatMapping[combSF[0]
                                         ]["history"][combSF[1]]["endTime"]
            tsSFDict[("Ts_SF", *combSF)].lowBound = None
            tsSFDict[("Ts_SF", *combSF)
                     ].setInitialValue(convertToTimeStamp(startTime))
            tsSFDict[("Ts_SF", *combSF)].fixValue()
            teSFDict[("Te_SF", *combSF)].lowBound = None
            teSFDict[("Te_SF", *combSF)
                     ].setInitialValue(convertToTimeStamp(endTime))
            teSFDict[("Te_SF", *combSF)].fixValue()

            tsRTDict[("Ts_RT", resource, slot)].lowBound = None
            tsRTDict[("Ts_RT", resource, slot)].setInitialValue(
                convertToTimeStamp(startTime))
            tsRTDict[("Ts_RT", resource, slot)].fixValue()
            teRTDict[("Te_RT", resource, slot)].lowBound = None
            teRTDict[("Te_RT", resource, slot)].setInitialValue(
                convertToTimeStamp(endTime))
            teRTDict[("Te_RT", resource, slot)].fixValue()
            preScheduledExecutions.append({"SF": combSF, "RT": (
                resource, slot), "startTime": startTime, "endTime": endTime})

    # * create a binary help variable ("y","RA1","t1")
    y = [("y", *combSF) for combSF in resSlotMapping]
    yDict = pulp.LpVariable.dicts("y", y, lowBound=0, upBound=1)

# * ----- Define constaints ----------
    msmoSP = pulp.LpProblem(
        "Multi-Stage_Multi-Order_Scheduling_Problem", pulp.LpMinimize)

    for combSF in specFeatureMapping:  # combSF = (spec, feat)

        # * Enforces that each feature only gets produced once over all timeslots
        msmoSP += pulp.lpSum([wDict[("W", *combSF, *combRT)]
                             for combRT in resSlotMapping]) == 1

        # * Enforces that the endTime is one duration after the startTime
        if combSF not in [comb["SF"] for comb in preScheduledExecutions]:
            msmoSP += teSFDict[("Te_SF", *combSF)] == tsSFDict[("Ts_SF", *combSF)] + \
                pulp.lpSum([wDict[("W", *combSF, *combRT)] * (specResFeatMapping[combSF[0]]["features"][combSF[1]][combRT[0]]["duration"] if combRT[0] in specResFeatMapping[combSF[0]]["features"][combSF[1]] else 0)
                            for combRT in resSlotMapping])

        # * Enforces the endTime to be limited
        msmoSP += teSFDict[("Te_SF", *combSF)] <= inf

    for combRT in resSlotMapping:  # combRT = (res, slot)
        msmoSP += pulp.lpSum([wDict[("W", *combSF, *combRT)]
                             for combSF in specFeatureMapping]) + yDict[("y", *combRT)] == 1

        if combRT not in [comb["RT"] for comb in preScheduledExecutions]:
            msmoSP += teRTDict[("Te_RT", *combRT)] == tsRTDict[("Ts_RT", *combRT)] + \
                pulp.lpSum([wDict[("W", *combSF, *combRT)] * (specResFeatMapping[combSF[0]]["features"][combSF[1]][combRT[0]]["duration"] if combRT[0] in specResFeatMapping[combSF[0]]["features"][combSF[1]] else 0)
                            for combSF in specFeatureMapping])

        # * Enforces the endTime to be limited
        msmoSP += teRTDict[("Te_RT", *combRT)] <= inf

    # * Enforces Time matching between slots and features
    for element in w:  # elmenent = ("W", spec, feat, res, slot)
        msmoSP += inf*(1-wDict[element]) >= (tsRTDict[("Ts_RT",
                                                       *element[3:5])] - tsSFDict[("Ts_SF", *element[1:3])])
       ## msmoSP += inf*(1-wDict[element]) >= (teRTDict[("Te_RT",
         #                                              *element[3:5])] - teSFDict[("Te_SF", *element[1:3])])
        msmoSP += inf*(1-wDict[element]) >= (tsSFDict[("Ts_SF",
                                                       *element[1:3])] - tsRTDict[("Ts_RT", *element[3:5])])
       # msmoSP += inf*(1-wDict[element]) >= (teSFDict[("Te_SF",
        #                                               *element[1:3])] - teRTDict[("Te_RT", *element[3:5])])

    # * Enforces order for preordered features and no overlapping for not defined features
    for combSFF in featureCombinations:  # comb = (spec, feat1, feat2)

        if combSFF[1:3] not in specResFeatMapping[combSFF[0]]["transitions"]:
            msmoSP += teSFDict[("Te_SF", *combSFF[0:3:2])
                               ] <= tsSFDict[("Ts_SF", *combSFF[0:2])]

        elif (combSFF[2], combSFF[1]) not in specResFeatMapping[combSFF[0]]["transitions"]:
            msmoSP += teSFDict[("Te_SF", *combSFF[0:2])
                               ] <= tsSFDict[("Ts_SF", *combSFF[0:3:2])]

        else:
            msmoSP += -inf*(1-bDict[combSFF]) <= tsSFDict[("Ts_SF",
                                                           *combSFF[0:2])] - teSFDict[("Te_SF", *combSFF[0:3:2])]
            msmoSP += inf*(bDict[combSFF]) >= tsSFDict[("Ts_SF",
                                                        *combSFF[0:2])] - teSFDict[("Te_SF", *combSFF[0:3:2])]
            msmoSP += -inf*(bDict[combSFF]) <= tsSFDict[("Ts_SF",
                                                         *combSFF[0:3:2])] - teSFDict[("Te_SF", *combSFF[0:2])]
            msmoSP += inf*(1-bDict[combSFF]) >= tsSFDict[("Ts_SF",
                                                          *combSFF[0:3:2])] - teSFDict[("Te_SF", *combSFF[0:2])]

    # * Enforces  no overlapping of slots at a Resource
    for combRTT in slotCompinations:
        msmoSP += -inf*(1-cDict[combRTT]) <= tsRTDict[("Ts_RT",
                                                       *combRTT[0:2])] - teRTDict[("Te_RT", *combRTT[0:3:2])]
        msmoSP += inf*(cDict[combRTT]) >= tsRTDict[("Ts_RT",
                                                    *combRTT[0:2])] - teRTDict[("Te_RT", *combRTT[0:3:2])]
        msmoSP += -inf*(cDict[combRTT]) <= tsRTDict[("Ts_RT",
                                                     *combRTT[0:3:2])] - teRTDict[("Te_RT", *combRTT[0:2])]
        msmoSP += inf*(1-cDict[combRTT]) >= tsRTDict[("Ts_RT",
                                                      *combRTT[0:3:2])] - teRTDict[("Te_RT", *combRTT[0:2])]

        # for (index, slot) in enumerate(slotMapping[res]):
        #   if len(slotMapping[res]) == index + 1: break
        #  msmoSP += tsRTDict[("Ts_RT", res, slotMapping[res][index + 1])] >= teRTDict[("Te_RT", res, slot)]

# * ----- Define Optimisation problem ---
   # msmoSP += pulp.lpSum([(pulp.lpSum([wDict[("W", spec, feature, *combRT)] * specResFeatMapping[spec]["features"][feature][combRT[0]]["duration"] for feature in specResFeatMapping[spec]["features"] for combRT in resSlotMapping if combRT[0] in specResFeatMapping[spec]["features"][feature].keys()]) + (teSFDict[("Te2", spec, "end")] - tsSFDict[("Ts2", spec, "start")])
    #                     * specResFeatMapping[spec]["timeCoeff"])/specResFeatMapping[spec]["priority"] for spec in specList])
    msmoSP += pulp.lpSum([(pulp.lpSum([wDict[("W", spec, feature, *combRT)] * specResFeatMapping[spec]["features"][feature][combRT[0]]["duration"] for feature in specResFeatMapping[spec]["features"] for combRT in resSlotMapping if combRT[0] in specResFeatMapping[spec]["features"][feature].keys()]) + (teSFDict[("Te_SF", spec, "end")])
                         * specResFeatMapping[spec]["timeCoeff"])/specResFeatMapping[spec]["priority"] for spec in specList])

# * ----- Solve and return output ----
    # msmoSP.writeLP("test.lp")
    msmoSP.solve()

    if msmoSP.status != 1:
        print("Optimal: 1 | Not Solved: 0 | Infeasable: -1 | Unbounded: -2 | Undefined: -3")
        raise Exception("Problem not solved! Error code "+str(msmoSP.status))

    #print(" ------------ ordered by spec ------------ ")
    count = 0
    for spec in specList:
        count += 1
        paAutomata[spec]["preferredTransitions"] = {}
        featureTimeArray = [(tsSFDict[("Ts_SF", spec, feature)].value(
        ), feature) for feature in specResFeatMapping[spec]["features"]]
        featureTimeArray.sort(key=lambda values: values[0])
        for (index, feature) in enumerate([pair[1] for pair in featureTimeArray]):
            resourceList = [combination[0] for combination in resSlotMapping if wDict[(
                "W", spec, feature, *combination)].value() == 1]
            resource = resourceList[0]
            paAutomata[spec]["preferredTransitions"][feature] = {
                "startTime": convertToISOFormat(featureTimeArray[index][0]),
                "endTime": convertToISOFormat(teSFDict[("Te_SF", spec, feature)].value()),
                "resource": resource,
                "process": specResFeatMapping[spec]["features"][feature][resource]["process"]
            }
    print("products: "+str(count))
        #print("-------------")
        #print(spec+":")
       # for feature in specResFeatMapping[spec]["features"]:
         #   implementation = [(combination) for combination in resSlotMapping if wDict[(
             #   "W", spec, feature, *combination)].value() == 1]
            #print("feature " + feature + " implemented at " +
            #      " and also ".join([comb[0] for comb in implementation]))
            #print("StartTime (spec/feature): "+convertToISOFormat(tsSFDict[("Ts_SF", spec, feature)].value()) + " | (res/slot): " + " / ".join(
          #      [convertToISOFormat(tsRTDict[("Ts_RT", *combination)].value()) for combination in implementation]))
            #print("EndTime (spec/feature): "+convertToISOFormat(teSFDict[("Te_SF", spec, feature)].value()) + " | (res/slot): " + " / ".join(
           #     [convertToISOFormat(teRTDict[("Te_RT", *combination)].value()) for combination in implementation]))
            #print("- - - - - - -")

    #print(" ------------ ordered by res ------------ ")
   # for res in resList:
        #print("------")
        #print(res+":")
    #    for slot in slotMapping[res]:
      #      implementation = [(combSF) for combSF in specFeatureMapping if wDict[(
     #           "W", *combSF, res, slot)].value() == 1]
            #print("slot "+slot + " has features " + str(implementation))
            #print("StartTime (res/slot): " +
       #           convertToISOFormat(tsRTDict[("Ts_RT", res, slot)].value()))
            #print("EndTime (res/slot): " +
        #          convertToISOFormat(teRTDict[("Te_RT", res, slot)].value()))
            #print(" - - - - - ")

    return paAutomata


if __name__ == "__main__":
    from routes.internal.raAutomata import getRaAutomata
    from routes.internal.paAutomata import getPaAutomata
    paAutomata = getPaAutomata()
    raAutomata = getRaAutomata()
    runMILP(paAutomata, raAutomata)
