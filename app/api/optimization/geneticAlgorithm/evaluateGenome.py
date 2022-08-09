def createScheduleFromChromosome(chromosome: dict):
    # TODO include start times
    # TODO include plant layout
    # TODO use timestamps
    schedule = {}
    priorityList = [(spec, chromosome[spec]["priority"])
                    for spec in chromosome]
    priorityList.sort(key=lambda s: s[1])

    for (spec, _) in priorityList:
        resourceChain = chromosome[spec]["resourceChain"]
        time = 0
        for element in resourceChain:
            resource = element["resource"]
            duration = element["expectedPerformance"]["duration"]
            process = element["process"]
            def makeSlot(start): return {
                "spec": spec, "process": process, "start": start, "end": start+duration}

            if resource not in schedule.keys():
                schedule[resource] = [makeSlot(time)]
                time = time + duration
            else:
                if schedule[resource][0]["start"] > time + duration:
                    schedule[resource].insert(0, makeSlot(time))
                    time = time + duration
                else:
                    for index, slot in enumerate(schedule[resource]):
                        if index + 1 < len(schedule[resource]):
                            if schedule[resource][index + 1]["start"] - slot["end"] > duration and slot["end"] > time:
                                schedule[resource].insert(
                                    index + 1, makeSlot(slot["end"]))
                                time = slot["end"] + duration
                                break
                        else:
                            schedule[resource].append(makeSlot(slot["end"]))
                            time = slot["end"] + duration
                            break

    return schedule

def evaluateSchedule(chromosome: dict, schedule: dict):
    totalEvaluation = 0
    for spec in chromosome:
        if spec == "evaluation": continue
        objectiveFunction = chromosome[spec]["objectiveFunction"]
        priority = chromosome[spec]["priority"]

        endTime = 0
        performances = {}
        for element in chromosome[spec]["resourceChain"]:
            for key in element["expectedPerformance"]:
                if key not in performances.keys():
                    performances[key] = 0
                performances[key] += element["expectedPerformance"][key]
            schedulePart = schedule[element["resource"]]
            for slot in schedulePart:
                if slot["spec"] == spec and slot["end"] > endTime:
                    endTime = slot["end"]
        performances["duration"] = endTime
        helpSum = 0
        for key in performances:
                if key in objectiveFunction.keys():
                    helpSum += performances[key] * objectiveFunction[key]
        totalEvaluation += 1/priority * helpSum

    return totalEvaluation




def evaluateGenome(genome: list):
    for chromosome in genome:
        if "evaluation" in chromosome.keys():
            del chromosome["evaluation"]
        schedule = createScheduleFromChromosome(chromosome)
        chromosome["evaluation"] = evaluateSchedule(chromosome, schedule)
    return genome
