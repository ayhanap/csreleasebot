#!/usr/bin/env python

import urllib
import json
import os
import requests
import logging

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

bambooBaseURL = "http://build.orioncb.com/rest/api/latest/"
buildNamesMap = {"beta":"DEPL-BET0", "prod":"DEPL-BET1", "ibank":"DEPL-IBD2"}

BAMBOO_PASS = os.environ['BAMBOO_PASS']
BAMBOO_USER = os.environ['BAMBOO_USER']

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
    if req.get("result").get("action") != "check-release-state":
        return {}
    res = makeWebhookResult(req)
    return res


def findBuildState(buildName, buildNumber):
    print buildName, buildNumber
    bambooBuildName = buildNamesMap.get(buildName)
    buildURL = bambooBaseURL + "result/" + str(bambooBuildName) + "/"
    if buildNumber is None:
        buildNumber = "latest"
    buildQueryResult = requests.get(buildURL + str(buildNumber), headers={'content-type': 'application/json','Accept': 'application/json'}, auth=(BAMBOO_USER, BAMBOO_PASS))
    buildQueryResultJSON = json.loads(buildQueryResult.text)
    logging.debug(buildQueryResultJSON)
    buildState = buildQueryResultJSON.get("state")
    buildNumber = buildQueryResultJSON.get("buildNumber")
    return buildNumber, buildState


def makeWebhookResult(req):
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

    buildNumberLatest, buildStateLatest = findBuildState(releaseName, None)
    if buildStateLatest == "Successful":
        buildNumberCurrent, buildStateCurrent = findBuildState(releaseName, buildNumberLatest+1)
        if buildStateCurrent is None:
            result = "Complete"
        elif buildStateCurrent == "Unknown":
            result = "Running"
        elif buildStateCurrent == "Successful":
            result = "Complete"
    else:
        result = "Failed"

    # print(json.dumps(item, indent=4))

    speech = releaseName + " release is " + result

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "csreleasebot"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
