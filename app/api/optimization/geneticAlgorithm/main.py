from optimization.geneticAlgorithm.getInitialData import getFeatureResourceMapping, createInitialGenome
from optimization.geneticAlgorithm.evaluateGenome import evaluateGenome, createScheduleFromChromosome
from optimization.geneticAlgorithm.evolveGenome import evolveGenome
import json

def runGA():
    featureResourceMapping = getFeatureResourceMapping()
    genomeSize = 1000
    genome = createInitialGenome(genomeSize, featureResourceMapping)
    iterations = 10
    for index in range(iterations):
        evaluateGenome(genome)
        genomeMapping = [(index , chromosome["evaluation"]) for index,chromosome in enumerate(genome)]
        genomeMapping.sort(key=lambda s: s[1],reverse=True)
        bestGenomeIndicies = [x[0] for x in genomeMapping[:30]]
        bestScore = genome[bestGenomeIndicies[0]]["evaluation"]
        worstScore = genome[genomeMapping[genomeSize - 1][0]]["evaluation"]

        print(str(index)+ " iteration-scores | best: "+str(round(bestScore))+" | worst: "+str(round(worstScore)))
        genome = evolveGenome(genome,bestGenomeIndicies,featureResourceMapping)

    bestChromosome = genome[bestGenomeIndicies[0]]
    schedule = createScheduleFromChromosome(bestChromosome)
    with open("solution.json", "w") as file:
       file.write(json.dumps({
           "bestChromosome": bestChromosome,
           "schedule": schedule
       }))

if __name__ == "__main__":
    runGA()