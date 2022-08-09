import stardog
from decouple import config
from fastapi import FastAPI
import time
import requests
from routes.internal import paAutomata, raAutomata, processExecutions, proposalRating
from routes.external import specifications, resources
from optimization.geneticAlgorithm.main import runGA

from initialisation import checkInitialConsistencies

fileName = config("FILENAME")
dbName = config("DBName")
baseURI = config("BASEURI")
baseDIR = config("BASEDIR")
conn_details = {
    'endpoint': config("SD_ENDPOINT"),
    'username': config("SD_USER"),
    'password': config("SD_PW")
}
docker = config("DOCKER")
app = FastAPI()
routers = [resources, paAutomata, raAutomata, specifications, processExecutions, proposalRating]
for route in routers:
    app.include_router(route.router)
#TODO add service functions, like checking if a spec is completed or only allowing an exit plan, if there is an invalid feature or order of features

@app.on_event("startup")
async def startUp():
    while True:
        try: 
            r = requests.get("http://stardog:5820/admin/status")
            if r.status_code == 401 or r.status_code == 200: break
        except:
            print("Waiting on StarDog")
            time.sleep(10)
    with stardog.Admin(**conn_details) as admin:
        if dbName in [db.name for db in admin.databases()]:
            admin.database(dbName).drop()
        admin.new_database(dbName)
        conn = stardog.Connection(dbName, **conn_details)
        conn.begin()
        conn.add(stardog.content.File(fileName))
        conn.commit()
        checkInitialConsistencies.checkInitialConsistencies(conn)
        conn.close()
    print("Startup complete - open the swagger documentation @ http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdownEven():
    with stardog.Admin(**conn_details) as admin:
        conn = stardog.Connection(dbName, **conn_details)
        content = str(conn.export())[2:-1].strip("\\t").split("\\n")
        with open("./result.ttl", "w") as file:
            file.write('\n'.join(content))
        db = admin.database(dbName)
        db.drop()


@app.get("/")
async def test():
    return "For the SwaggerUI open 127.0.0.1:8000/docs"


@app.get("/testGA")
async def ga():
    return runGA()