import stardog
from decouple import config

dbName = config("DBName")
baseURI = config("BASEURI")
baseDIR = config("BASEDIR")
conn_details = {
    'endpoint': config("SD_ENDPOINT"),
    'username': config("SD_USER"),
    'password': config("SD_PW")
}

def runSelectQuery(query, reasoningBool = False):
    with stardog.Connection(dbName, **conn_details) as conn:
        conn.begin(reasoning = reasoningBool)
        result = conn.select(query, reasoning = reasoningBool)
        conn.commit()
        return result if result else "No Results!"

def runAskQuery(query, reasoningBool = True):
    with stardog.Connection(dbName, **conn_details) as conn:
        conn.begin(reasoning = reasoningBool)
        result = conn.ask(query, reasoning=reasoningBool)
        conn.commit()
        return result 

def runUpdateQuery(query, reasoningBool = True):
    with stardog.Connection(dbName, **conn_details) as conn:
        conn.begin(reasoning = reasoningBool)
        conn.update(query, reasoning = reasoningBool)
        conn.commit()
        return "Success"
