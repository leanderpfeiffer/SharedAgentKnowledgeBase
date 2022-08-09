# Running the API on Windows

## Installing StarDog

In order to successfully run the API, StarDog has to be installed and running.
For documentation and the corresponding download link, look [here](https://docs.stardog.com/get-started/install-stardog/windows-installation).

## Creating the virtual environement

As .sh scripts don't run natively on windows, you will have to manually initialize the virtual environemt (venv).
For this, make sure you have at least version 3.9 of python installed and the a somewhat recent version of pip.
To initialize the venv, run ```python -m venv venv``` insdide the agent-ontology-dev directory using Powershell.
Then, activate the venv by running ```.\venv\Scripts\activate.bat```, inside a powershell window.
Finally, you can install all requirements by running ```pip3 install -r requirements.txt``` in the same window.

## Change the Base Directory

In order for all scripts to work as their intended, change up the BASEDIR variable inside the .env file to your corresponding system path of the repository.
If you can find it, open the project directory using a editor, like VSCode.

## Starting the API

If everything worked correctly, make sure the venv is active.
In case its not running, run the previous mentioned command again.
To start the API run ```python -m uvicorn main:app --reload```.
