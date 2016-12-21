#!/usr/bin/env python

import json
import os
import requests
import logging
import datetime as dt
import pytz

from enum import Enum

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

bambooBaseURL = "http://build.orioncb.com/rest/api/latest/"
buildNamesMap = {"beta": "DEPL-BET0", "prod": "DEPL-BET1", "alfa": "DEPL-GEN1", "dev": "DEPL-GEN0", "ibank": "DEPL-IBD2"}
buildSchedulesMap = {
    "beta": [dt.time(7, 0, 0), dt.time(12, 0, 0), dt.time(16, 0, 0), dt.time(19, 0, 0)],
    "prod": [dt.time(12, 0, 0), dt.time(22, 0, 0)],
    "dev": [dt.time(10, 0, 0), dt.time(11, 0, 0), dt.time(12, 0, 0), dt.time(14, 0, 0),
                  dt.time(15, 0, 0), dt.time(16, 0, 0), dt.time(17, 0, 0), dt.time(18, 0, 0),
                  dt.time(19, 0, 0), dt.time(20, 0, 0), dt.time(21, 0, 0)],
    "alfa": [dt.time(10, 30, 0), dt.time(12, 30, 0), dt.time(15, 30, 0), dt.time(17, 30, 0),
                  dt.time(19, 30, 0), dt.time(20, 30, 0), dt.time(21, 30, 0), dt.time(22, 30, 0)],
    "ibank": [dt.time(0, 0, 0)],
                     }

BAMBOO_PASS = os.environ['BAMBOO_PASS']
BAMBOO_USER = os.environ['BAMBOO_USER']


class Build(object):
    buildState = None
    buildNumber = None
    buildStartedTime = None
    buildCompletedTime = None
    buildRelativeTime = None
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
    build.buildRelativeTime = buildQueryResultJSON.get("buildRelativeTime")
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

def findNextBuildTime(buildName):
    currTime = dt.datetime.now(pytz.timezone('Europe/Istanbul'))
    for buildTime in buildSchedulesMap.get(buildName):
        timeToNextBuild =  dt.timedelta(hours=buildTime.hour, minutes=buildTime.minute, seconds=buildTime.second) - \
              dt.timedelta(hours=currTime.hour, minutes=currTime.minute, seconds=currTime.minute)
        if timeToNextBuild > dt.timedelta():
            print timeToNextBuild
            return timeToNextBuild, buildTime

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

def getParameter(parameters, contextParameters, parameterName):
    parameter = parameters.get(parameterName)
    if parameter is None:
        if contextParameters is not None:
            parameter = contextParameters.get(parameterName)
    return parameter


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
    contexts = result.get('contexts')
    contextParameters = None
    for context in contexts:
        if context.get('name') == 'release-name-context':
            contextParameters = context.get('parameters')

    if parameters is None:
        return {}

    releaseName = getParameter(parameters,contextParameters, 'release-name')

    tense = getParameter(parameters,contextParameters, 'tense')

    releaseState = getParameter(parameters,contextParameters, 'release-state')

    result, build = findBuildState(releaseName)
    speech = "I don't know"
    if releaseState == 'complete':
        if tense == 'future':
            if result == BuildState.COMPLETE:
                speech = releaseName + " release is already completed " + build.buildRelativeTime + "."
            elif result == BuildState.RUNNING:
                speech = releaseName + " release will be completed in " + build.prettyTimeRemaining
        elif tense == 'past':
            if result == BuildState.COMPLETE:
                speech = releaseName + " release is completed " + build.buildRelativeTime + "."
            elif result == BuildState.RUNNING:
                speech = releaseName + " release will be completed in " + build.prettyTimeRemaining
    elif releaseState == 'running':
        if tense == 'future':
            if result == BuildState.COMPLETE:
                timeToNextBuild, buildTime = findNextBuildTime(releaseName)
                speech = releaseName + " release will start in " + str(timeToNextBuild) + " hours." #TODO: beautify time text
            elif result == BuildState.RUNNING:
                speech = releaseName + " release started " + build.prettyStartedTime
        elif tense == 'past':
            if result == BuildState.COMPLETE:
                speech = releaseName + " release completed " + build.buildRelativeTime + "."
            elif result == BuildState.RUNNING:
                speech = releaseName + " release started " + build.prettyStartedTime
        else:
            speech = "I don't know"
    elif releaseState == 'failed':
        speech = "I don't know"
    else:
        if tense == 'future':
            timeToNextBuild, buildTime = findNextBuildTime(releaseName)
            speech = releaseName + " release will start in " + str(timeToNextBuild) + " hours." #TODO: beautify time text
        elif tense == 'past':
            if result == BuildState.COMPLETE:
                speech = releaseName + " release completed " + build.buildRelativeTime + "."
            elif result == BuildState.RUNNING:
                speech = releaseName + " release started " + build.prettyStartedTime

    return makeCommonResponse(speech)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=os.environ['FLASK_DEBUG'], port=port, host='0.0.0.0')
