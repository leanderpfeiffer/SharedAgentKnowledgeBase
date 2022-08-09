from decouple import config
ontoName = config("BASEURI")

def format(key): return "<" + key + ">"

nameSpaces = """
prefix : <http://PAonto.com#> 
prefix owl: <http://www.w3.org/2002/07/owl#> 
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> 
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
    """

def changeValues(query, data):
    """Mapps a Query with replaceable parameters in <braces> with their 
        according values from a dictionary"""
    
    for key in data:
        if type(data[key]) == str:
            query = query.replace(format(key), ":"+data[key])
        elif isinstance(data[key],dict):
            query = changeValues(query, data[key])
        elif type(data[key]) == list:
            query = query.replace(format(key), ", ".join([":"+x for x in data[key]]))
        elif type(data[key]) == bool:
            query = query.replace(format(key), str(data[key]).lower())
        else: 
            query = query.replace(format(key), '"'+str(data[key]).replace(" ","T")+'"') #TODO add type seperation
    return  query

def createQuery(baseQuery, data):
    query = changeValues(baseQuery,data)
    return nameSpaces + query 

def createQueryFromFile(queryName, directory, data):
    with open(directory +"/"+ queryName+".sparql") as file:
        baseQuery = file.read()
        return createQuery(baseQuery,data)


def readQuery(queryName, directory):
    with open(directory +"/"+ queryName+".sparql") as file:
        return nameSpaces + file.read()

def getValue(element, key):
    return element[key]["value"].replace(ontoName,"")
