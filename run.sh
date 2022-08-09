#!/bin/sh

STARDOG="/Users/leanderpfeiffer/StardogHome/"
AOD="/Users/leanderpfeiffer/Desktop/BA/agent-ontology-dev/"


cd "$STARDOG/"
stardog-admin server start
sleep 5

source "$AOD/venv/bin/activate"
pip3 install -r "$AOD/requirements.txt"

cd "$AOD/app/api"
uvicorn main:app --reload

# ---------------------------------- #
#                                    #
#          ##                        #
#          ##                        #
#          ##      #####             #
#          ##      ##   ##           #
#          ##      ##    ##          #
#          ##      ##   ##           #
#          #############             #
#                  ##                #
#                  ##                #
#                  ##                #
#                 ##                 #
#                                    #
#       Code brought to you by       #
#         Leander Pfeiffer           #
# https://github.com/leanderpfeiffer #
#                                    #
# ---------------------------------- #