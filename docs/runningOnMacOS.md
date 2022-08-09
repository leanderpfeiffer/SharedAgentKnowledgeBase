# Running the API on macOS

* Install Stardog and make sure it's activated

* Open the .env file and change the following parts:

  * The BASEDIR and APIDIR to your System-path of this directory

  * The Stardog (SD) Endpoint, User and Password to fit your Stardog configuration

* Open the run.sh file and change the following parts:

  * The STARDOG-Variable to your systempath of Stardog-home

  * The AOD-Variable to your System-path of this directory (Same as BASEDIR)

* Setup a Python environment in the basedirectory using the command ```python3 -m venv /venv```

* Run ```sh run.sh``` and enjoy!
