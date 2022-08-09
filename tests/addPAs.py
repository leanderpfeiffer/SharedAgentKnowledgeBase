import requests
import random
import uuid


def ot(): return str(random.randint(1,2))
def co(): return random.randrange(1, 10)


def main():
    agents = 5
    for i in range(agents):
        body = {
            "id": "product" + str(uuid.uuid4()),
            "specification": "specTypeA",
            "deadline": "2023-08-03T23:59:59.047Z",
            "features": ["Fd"+ot(), "Fi"+ot(), "Fl"+ot()],
            "objectiveFunction": {
                "timeCoeff": co(),
                "costCoeff": co(),
                "emissionCoeff": co(),
                "qualityCoeff": co()
            },
            "priority": 1
        }
        #print(body)
        requests.post('http://127.0.0.1:8000/spec/add', json=body)
        print("Added product"+str(i))


if __name__ == '__main__':
    main()
