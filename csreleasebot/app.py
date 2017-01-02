#!/usr/bin/env python

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
from csreleasebot import BambooAdapter
from csreleasebot import JiraAdapter

app = Flask(__name__)


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
        return BambooAdapter.checkReleaseState(req)
    elif result.get("action") == "check-release-time":
        return BambooAdapter.checkReleaseTime(req)
    elif result.get("action") == "check-issue-state":
        return JiraAdapter.checkIssueState(req)
    elif result.get("action") == "check-issue-deployment":
        return JiraAdapter.checkIssueDeploymentState(req)
    else:
        return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=os.environ['FLASK_DEBUG'], port=port, host='0.0.0.0')
