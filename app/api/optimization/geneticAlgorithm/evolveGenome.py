from copy import deepcopy
from random import randint, randrange, choice


def crossOverChromosomes(chromosome1, chromosome2):
    newChromosome = {}

    for spec in chromosome1:
        if randint(0,1) == 1 and spec != "evaluation":
            newChromosome[spec] = deepcopy(chromosome1[spec])
        elif spec != "evaluation":
            newChromosome[spec] = deepcopy(chromosome2[spec])
    return newChromosome

def mutateChromosome(chromosome, featureResourceMapping):
    newChromosome = {}
    newChromosome = deepcopy(chromosome)
    for spec in newChromosome:
        # 1/10 chance of a general mutation
        if randint(0,5) == 0 and spec != "evaluation":
            
            if randint(0,3) == 0:
                # 1/4 chance of changing whole production order
                possibleFeatureChains = newChromosome[spec]["possibleFeatureChains"]
                selectedFeatureChain = choice(possibleFeatureChains)

                selectedResourceChain = []
                for feature in selectedFeatureChain:
                    possibleResources = featureResourceMapping[feature]
                    selectedResourceChain.append(choice(possibleResources))

                newChromosome[spec]["resourceChain"] = selectedResourceChain
        
            else:
                # 3/4 chance of changing only one Resource
                changingResourceIndex = randrange(0,len(newChromosome[spec]["resourceChain"]))
                feature = newChromosome[spec]["resourceChain"][changingResourceIndex]["feature"]
                possibleResources = featureResourceMapping[feature]
                newResource = choice(possibleResources)
                newChromosome[spec]["resourceChain"][changingResourceIndex] = newResource

    return newChromosome


def evolveGenome(genome, bestIndicies, featureResourceMapping):
    crossOvers = 80
    mutations = 20
    survivingGenome = [deepcopy(genome[index]) for index in bestIndicies]

    for index in range(len(genome)):
        if randint(0,crossOvers + mutations) < mutations:
            genome[index] = mutateChromosome(choice(survivingGenome),featureResourceMapping)
        else: 
            genome[index] = crossOverChromosomes(choice(survivingGenome),choice(survivingGenome))

    return genome

