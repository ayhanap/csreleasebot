#!/usr/bin/env python

import urllib
import json
import os
import requests
import logging

from enum import Enum

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

bambooBaseURL = "http://build.orioncb.com/rest/api/latest/"
buildNamesMap = {"beta":"DEPL-BET0", "prod":"DEPL-BET1", "alfa":"DEPL-GEN1", "dev":"DEPL-GEN0", "ibank":"DEPL-IBD2"}

BAMBOO_PASS = os.environ['BAMBOO_PASS']
BAMBOO_USER = os.environ['BAMBOO_USER']


class Build(object):
    buildState = None
    buildNumber = None
    buildStartedTime = None
    buildCompletedTime = None
    percentageCompletedPretty = None
    prettyTimeRemaining = None
    startedTime = None
    prettyStartedTime = None


class BuildState(Enum):
    COMPLETE = 'Complete'
    RUNNING = 'Running'
    FAILED = 'Failed'



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    result = req.get("result")
    if result.get("action") == "check-release-state":
        return checkReleaseState(req)
    elif result.get("action") == "check-release-time":
        return checkReleaseTime(req)
    else:
        return {}


def findSingleBuildState(buildName, buildNumber):
    print buildName, buildNumber
    bambooBuildName = buildNamesMap.get(buildName)
    buildURL = bambooBaseURL + "result/" + str(bambooBuildName) + "/"
    if buildNumber is None:
        buildNumber = "latest"
    buildQueryResult = requests.get(buildURL + str(buildNumber), headers={'content-type': 'application/json','Accept': 'application/json'}, auth=(BAMBOO_USER, BAMBOO_PASS))
    buildQueryResultJSON = json.loads(buildQueryResult.text)
    logging.debug(buildQueryResultJSON)
    build = Build()
    build.buildState = buildQueryResultJSON.get("state")
    build.buildNumber = buildQueryResultJSON.get("buildNumber")
    build.buildStartedTime = buildQueryResultJSON.get("buildStartedTime")
    build.buildCompletedTime = buildQueryResultJSON.get("buildCompletedTime")
    progress = buildQueryResultJSON.get("progress")
    if progress is not None:
        build.percentageCompletedPretty = progress.get("percentageCompletedPretty")
        build.prettyTimeRemaining = progress.get("prettyTimeRemaining")
        build.startedTime = progress.get("startedTimeFormatted")
        build.prettyStartedTime = progress.get("prettyStartedTime")
    return build


def findBuildState(buildName):
    buildLatest = findSingleBuildState(buildName, None)
    result = None
    build = None
    if buildLatest.buildState == "Successful":
        buildCurrent = findSingleBuildState(buildName, buildLatest.buildNumber + 1)
        if buildCurrent.buildState is None:
            result = BuildState.COMPLETE
            build = buildLatest
        elif buildCurrent.buildState == "Unknown":
            result = BuildState.RUNNING
            build = buildCurrent
        elif buildCurrent.buildState == "Successful":
            result = BuildState.COMPLETE
            build = buildCurrent
    else:
        result = BuildState.FAILED
        build = buildLatest
    return result, build


def makeCommonResponse(speech):
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "csreleasebot"
    }


def checkReleaseState(req):
    result = req.get("result")
    parameters = result.get('parameters')
    if parameters is None:
        return {}

    releaseName = parameters.get('release-name')
    if releaseName is None:
        return {}

    releaseState = parameters.get('release-state')
    if releaseState is None:
        return {}

    result, build = findBuildState(releaseName)
    speech = releaseName + " release is " + result.value
    return makeCommonResponse(speech)

def checkReleaseTime(req):
    result = req.get("result")
    parameters = result.get('parameters')
    if parameters is None:
        return {}

    releaseName = parameters.get('release-name')
    if releaseName is None:
        return {}

    releaseState = parameters.get('release-state')

    result, build = findBuildState(releaseName)
    speech = "I don't know"
    if releaseState == 'complete':
        if result == BuildState.COMPLETE:
            speech = releaseName + " release is already Completed."
        elif result == BuildState.RUNNING:
            speech = releaseName + " realease will be completed in " + build.prettyTimeRemaining
    elif releaseState == 'running':
        if result == BuildState.COMPLETE:
            speech = releaseName + " release is already Completed."
        elif result == BuildState.RUNNING:
            speech = releaseName + " realease started " + build.prettyStartedTime
    elif releaseState == 'failed':
        speech = "I don't know"
    else:
        speech = "I don't know"

    return makeCommonResponse(speech)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=os.environ['FLASK_DEBUG'], port=port, host='0.0.0.0')
