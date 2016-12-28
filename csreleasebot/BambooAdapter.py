import datetime as dt
import os
import json

import logging
import pytz
import requests
from enum import Enum

from csreleasebot import Common

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
    lifeCycleState = None
    percentageCompletedPretty = None
    prettyTimeRemaining = None
    startedTime = None
    prettyStartedTime = None


class BuildState(Enum):
    COMPLETE = 'Complete'
    RUNNING = 'Running'
    FAILED = 'Failed'


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
    build.lifeCycleState = buildQueryResultJSON.get("lifeCycleState")
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
        elif buildCurrent.buildState == "Unknown" and buildCurrent.lifeCycleState == 'InProgress':
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
        nextBuildTime = dt.timedelta(hours=buildTime.hour, minutes=buildTime.minute, seconds=buildTime.second) - \
                           dt.timedelta(hours=currTime.hour, minutes=currTime.minute, seconds=currTime.minute)
        if nextBuildTime > dt.timedelta():
            print nextBuildTime
            return nextBuildTime, buildTime


def checkReleaseState(req):
    result = req.get("result")
    parameters = result.get('parameters')
    if parameters is None:
        return {}

    releaseName = Common.getParameter(req, 'release-name-context', 'release-name')
    if releaseName is None:
        return {}

    releaseState = Common.getParameter(req, 'release-name-context', 'release-state')
    if releaseState is None:
        return {}

    result, build = findBuildState(releaseName)
    speech = "%s release is %s" % (releaseName, result.value)
    return Common.makeCommonResponse(speech)


def timeToNextBuild(parameters):
    releaseName = parameters.get('releaseName')
    timeToNextBuildVar, buildTime = findNextBuildTime(releaseName)
    return str(timeToNextBuildVar) #TODO: beautify time text


def checkReleaseTime(req):
    result = req.get("result")
    parameters = result.get('parameters')

    if parameters is None:
        return {}

    releaseName = Common.getParameter(req, 'release-name-context', 'release-name')

    tense = Common.getParameter(req, 'release-name-context', 'tense')

    askedReleaseState = Common.getParameter(req, 'release-name-context', 'release-state')

    currentBuildState, build = findBuildState(releaseName)

    matchParameters = {'askedBuildState': askedReleaseState, 'tense': tense, 'currentBuildState': currentBuildState.value}

    message = Common.getMessageFromFile('csreleasebot/outputs.yaml', 'checkTimeResults', matchParameters)

    message = Common.fillParameters({'releaseName': releaseName, 'build': build, 'timeToNextBuild': timeToNextBuild}, message)

    speech = message

    return Common.makeCommonResponse(speech)