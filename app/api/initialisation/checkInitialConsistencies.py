from decouple import config

DIR = config("APIDIR")+ "/initialisation/"
baseURI = config("BASEURI")


def createInconsistencyError(inconsistencies):
    errorMessages = []
    for inconsistency in inconsistencies:
        spec = inconsistency["spec"]["value"].strip(baseURI)
        feat1 = inconsistency["feat1"]["value"].strip(baseURI)
        feat2 = inconsistency["feat2"]["value"].strip(baseURI)
        confType = inconsistency["type"]["value"]
        errorMessages.append(spec + " has a " + confType +
                             " concerning the following feature(s): "+feat1 + ", " + feat2)
    return '\n'.join(errorMessages)




def checkInitialConsistencies(connection):
    queryName = DIR + "featConsistency.sparql"
    with open(queryName,"r") as queryFile:
        query = queryFile.read()
        result = connection.select(query)
        if len(result["results"]["bindings"]) != 0:
            print(createInconsistencyError(result["results"]["bindings"]))
