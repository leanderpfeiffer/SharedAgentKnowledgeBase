#!/usr/bin/env python3
"""convert standardized csv files to owl ontology"""

import csv
from decouple import config
from os import listdir
from owlready2 import *
import types
import datetime

#DIR = '../csvsPAonto/'
DIR = config("BASEDIR")+"/app/ontologyBuilder/csvsPAonto/"
BASEURI = config("BASEURI")
FILEDIR = config("BASEDIR")+"/app/api/"

dataTypes = {"xsd:float": float, "xsd:str": str, "xsd:int": int,
             "xsd:dateTime": datetime.datetime, "xsd:bool": bool}


def file_content_to_dict(file_names):
    fileDict = {}
    for file_name in file_names:
        fileDict[file_name] = csv_to_array(file_name)
    return fileDict


def find_csv_filenames(path_dir, suffix=".csv"):
    """get all filenames with suffix .csv from the specified directory"""
    filenames = listdir(path_dir)
    return [filename for filename in filenames if filename.endswith(suffix) and not filename.startswith("_")]


def csv_to_array(csv_name):
    """import data from csv and return as an array"""
    file_path = DIR+csv_name
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        return list(csv_reader)


def create_classes(classesCSV, onto):
    """Dynamicly creates Classes according to Classes spreadsheet"""
    classes = {}

    for y_coord in range(4, len(classesCSV)):
        className = classesCSV[y_coord][2]
        classes[className] = types.new_class(className, (Thing,))

    for x_coord in range(3, len(classesCSV[0])):
        if classesCSV[2][x_coord] == "":
            continue
        topClassName = (classesCSV[3][x_coord][1:])
        for y_coord in range(4, len(classesCSV)):
            subClassName = classesCSV[y_coord][x_coord]
            if subClassName:
                classes[subClassName] = types.new_class(
                    subClassName, (classes[topClassName], ))

    return (onto, classes)


def create_object_properties(objectPropertiesCSV, onto, classes):
    """Dynamicly creates ObjectProperties according to ObjectProperties spreadsheet"""

    propertyDef = {
        "owl:ObjectProperty": ObjectProperty,
        "owl:TransitiveProperty": TransitiveProperty,
        "owl:SymmetricProperty": SymmetricProperty,
        "owl:FunctionalProperty": FunctionalProperty,
        "owl:InverseFunctionalProperty": InverseFunctionalProperty,
        "owl:AsymmetricProperty": AsymmetricProperty,
        "owl:ReflexiveProperty": ReflexiveProperty,
        "owl:IrreflexiveProperty": IrreflexiveProperty
    }
    objectProperties = {}
    for y_coord in range(4, len(objectPropertiesCSV)):
        objectPropertyName = objectPropertiesCSV[y_coord][2]
        props = []
        for x_coord in range(3, len(objectPropertiesCSV[y_coord])):
            if objectPropertiesCSV[y_coord][x_coord] == "x" and (x_coord == 3 or x_coord > 6):
                propName = objectPropertiesCSV[3][x_coord]
                props.append(propertyDef[propName])
            elif x_coord == 4 and objectPropertiesCSV[y_coord][x_coord] != "":
                propName = objectPropertiesCSV[y_coord][x_coord]
                props.append(
                    objectProperties[propName] if propName in objectProperties else None)

        objectProperties[objectPropertyName] = types.new_class(
            objectPropertyName, (*props,))

        if objectPropertiesCSV[y_coord][5] != "":
            domainName = objectPropertiesCSV[y_coord][5]
            objectProperties[objectPropertyName].domain = classes[domainName[1:]]
        if objectPropertiesCSV[y_coord][6] != "":
            rangeName = objectPropertiesCSV[y_coord][6]
            objectProperties[objectPropertyName].range = classes[rangeName[1:]]

    return (onto, objectProperties)


def create_datatype_properties(datatypePropertiesCSV, onto, classes):
    datatypeProperties = {}

    for y_coord in range(4, len(datatypePropertiesCSV)):
        csvProps = datatypePropertiesCSV[y_coord][2:]
        propertyName = csvProps[0]
        props = []
        if csvProps[1] == "x":
            props.append(DatatypeProperty)
        if csvProps[2] != "":
            props.append(datatypeProperties[csvProps[2][1:]])
        if csvProps[5] == "x":
            props.append(FunctionalProperty)
        datatypeProperties[propertyName] = types.new_class(
            propertyName, (*props,))
        if csvProps[3] != "":
            datatypeProperties[propertyName].domain = classes[csvProps[3][1:]]
        if csvProps[4] != "":
            datatypeProperties[propertyName].range = dataTypes[csvProps[4]]
    return (onto, datatypeProperties)


def create_instances(instancesCSV, onto, classes):
    instances = {}

    for x_coord in range(2, len(instancesCSV[0]), 3):
        for y_coord in range(4, len(instancesCSV)):
            instanceName = instancesCSV[y_coord][x_coord+1]
            if instanceName == "":
                continue
            if instancesCSV[y_coord][x_coord] != "":
                className = instancesCSV[y_coord][x_coord]
            instances[instanceName] = classes[className](instanceName)
    return (onto, instances)


def matrix_into_onto(documentCSV, onto, ontoDict):
    onto.classes()
    onto.properties()
    propertyName = documentCSV[2][2][1:]
    functionalProperty = issubclass(ontoDict[propertyName], FunctionalProperty)
    for y_coord in range(4, len(documentCSV)):
        objElementList = []
        subjElement = documentCSV[y_coord][3]
        for x_coord in range(4, len(documentCSV[y_coord])):
            if documentCSV[y_coord][x_coord] == "x":
                objElementList.append(ontoDict[documentCSV[3][x_coord]])

        if len(objElementList) == 1 and functionalProperty:
            setattr(ontoDict[subjElement], propertyName, objElementList[0])
        elif len(objElementList) != 0:
            setattr(ontoDict[subjElement], propertyName, objElementList)
    return onto


def metamatrix_into_onto(documentCSV, onto, ontoDict):
    onto.classes()
    onto.properties()
    connectionName = documentCSV[2][2][1:]
    for y_coord in range(4, len(documentCSV)):
        subjElement = documentCSV[y_coord][3]
        for x_coord in range(4, len(documentCSV[y_coord])):
            if documentCSV[y_coord][x_coord] == "x":
                objElement = documentCSV[3][x_coord]
                ontoDict[subjElement].is_a.append(
                    ontoDict[connectionName].some(ontoDict[objElement]))

    return onto


def smatrix_into_onto(documentCSV, onto, ontoDict):
    onto.classes()
    onto.properties()

    for y_coord in range(4, len(documentCSV)):
        propDict = {}
        subjElement = documentCSV[y_coord][2]
        for x_coord in range(3, len(documentCSV[0])):
            propertyName = documentCSV[3][x_coord][1:]
            objElement = documentCSV[y_coord][x_coord]
            if propertyName not in propDict.keys():
                propDict[propertyName] = ontoDict[objElement] if issubclass(ontoDict[propertyName], FunctionalProperty) else [ontoDict[objElement]]
            else:
                propDict[propertyName] = [ *propDict[propertyName], ontoDict[objElement]]
        for key in propDict:
            setattr(ontoDict[subjElement], propertyName, propDict[key])
   
    return onto


def func_into_onto(documentCSV, onto, ontoDict):
    onto.classes()
    onto.properties()
    for x_coord in range(4, len(documentCSV[0])):
        if not documentCSV[2][x_coord]:
            continue  # Continue if table column is empty
        convertValue = dataTypes[documentCSV[3][x_coord][2:]]
        for y_coord in range(4, len(documentCSV)):
            if documentCSV[y_coord][x_coord]:
                if convertValue == datetime.datetime:
                    value = datetime.datetime.fromisoformat(
                        documentCSV[y_coord][x_coord])
                else:
                    value = convertValue(documentCSV[y_coord][x_coord])
                setattr(ontoDict[documentCSV[y_coord][2]],
                        documentCSV[2][x_coord][1:], value)
    return onto


def buildOntologyFromCSV(fileName):
    file_names = find_csv_filenames(DIR)
    csv_data = file_content_to_dict(file_names)

    onto = get_ontology(BASEURI)
    with onto:
        file_names.remove("0Prefixes.csv")

        (onto, classes) = create_classes(csv_data["1Classes.csv"], onto)
        file_names.remove("1Classes.csv")

        (onto, objectProperties) = create_object_properties(
            csv_data["2ObjectProperties.csv"], onto, classes)
        file_names.remove("2ObjectProperties.csv")

        (onto, datatypeProperties) = create_datatype_properties(
            csv_data["3DatatypeProperties.csv"], onto, classes)
        file_names.remove("3DatatypeProperties.csv")

        (onto, instances) = create_instances(
            csv_data["4Instances.csv"], onto, classes)
        file_names.remove("4Instances.csv")

        ontoDict = {**classes, **objectProperties,
                    **datatypeProperties, **instances}

        for element in file_names:
            if csv_data[element][0][0] == "matrix":
                onto = matrix_into_onto(csv_data[element], onto, ontoDict)
            elif csv_data[element][0][0] == "metamatrix":
                onto = metamatrix_into_onto(csv_data[element], onto, ontoDict)
            elif csv_data[element][0][0] == "func":
                onto = func_into_onto(csv_data[element], onto, ontoDict)
            elif csv_data[element][0][0] == "smatrix":
                onto = smatrix_into_onto(csv_data[element], onto, ontoDict)

        onto.save(file=fileName, format="rdfxml")
        print("Created Initial Ontology!")
    return onto


if __name__ == "__main__":
    buildOntologyFromCSV(FILEDIR + "onto.owl")
