# -*- coding: utf-8 -*-
import json
import os

import logging

import dateutil.parser
import datetime as dt

import pytz
import requests

from csreleasebot import BambooAdapter
from csreleasebot import Common

jiraBaseURL = "http://issues.orioncb.com/rest/api/2/"

JIRA_USER = os.environ['BAMBOO_USER']
JIRA_PASS = os.environ['BAMBOO_PASS']


class Issue(object):

    def __init__(self):
        self.key = None
        self.id = None
        self.statusName = None
        self.statusCategoryId = None
        self.resolutionName = None
        self.resolutionId = None
        self.links = []
        self.resolutionDate = None
        self.changelog = []
        self.deploymentTimeSelection = None
        self.isInit = False

    @classmethod
    def fromIssueNo(cls, issueNo):
        issueJSON = Issue.getIssueJSON(issueNo)
        issue = Issue.fromIssueJSON(issueJSON)
        issue.links = Issue.getIssueLinksFromIssueJSON(issueJSON)
        issue.isInit = True
        return issue

    @classmethod
    def fromIssueJSON(cls, issueJSON):
        issue = Issue()
        issue.key = issueJSON.get('key')
        issue.id = issueJSON.get('id')
        fields = issueJSON.get('fields')
        issue.statusName = fields.get('status').get('name')
        issue.statusCategoryId = fields.get('status').get('statusCategory').get('id')

        resolutionDate = fields.get('resolutiondate')
        if resolutionDate is not None:
            issue.resolutionDate = dateutil.parser.parse(resolutionDate)

        resolution = fields.get('resolution')
        if resolution is not None:
            issue.resolutionName = resolution.get('name')
            issue.resolutionId = int(resolution.get('id'))

        deploymentTimeSelection = fields.get('customfield_10500')
        if deploymentTimeSelection is not None:
            issue.deploymentTimeSelection = deploymentTimeSelection.get('value')

        changelog = issueJSON.get('changelog')
        if changelog is not None:
            histories = changelog.get('histories')
            for history in histories:
                items = history.get('items')
                for item in items:
                    issue.changelog.append({'changeDate': history.get('created'), 'item': item})
        return issue

    # fills sub variables if didnt exist at the creation
    def __getattribute__(self, name):
        if not super(Issue, self).__getattribute__('isInit'):
            val = super(Issue, self).__getattribute__(name)
            if val is None:
                self.__dict__.update(self.fromIssueNo(self.key).__dict__)
                print("INIT!")
                return super(Issue, self).__getattribute__(name)
            return val
        return super(Issue, self).__getattribute__(name)

    def getLastReleaseIssue(self):
        if self.getProjectKey() == 'CDBR':
            return self
        releaseIssueLinks = []
        for issueLink in self.links:
            if issueLink.getProjectKey() == 'CDBR':
                releaseIssueLinks.append(issueLink)
        releaseIssueLinks.sort(key=lambda x: x.key, reverse=True)
        if not releaseIssueLinks:
            return None
        return releaseIssueLinks[0]

    def getProjectKey(self):
        return Issue.getIssueProjectKeyFromIssueNo(self.key)

    @property
    def isDeployed(self):
        if self.getProjectKey() == 'CDBR':
            return self.statusCategoryId == 3 and self.resolutionId == 1
        else:
            lastReleaseIssue = self.getLastReleaseIssue()
            if lastReleaseIssue is None:
                return False
            else:
                return lastReleaseIssue.isDeployed

    @property
    def deploymentDate(self):
        if self.isDeployed:
            if self.getProjectKey() == 'CDBR':
                return self.resolutionDate
            else:
                lastReleaseIssue = self.getLastReleaseIssue()
                return lastReleaseIssue.deploymentDate
        else:
            return None

    @property
    def timeToNextDeployment(self):
        lastReleaseIssue = self.getLastReleaseIssue()
        if lastReleaseIssue is None:
            return None
        elif lastReleaseIssue.statusName == 'Ready To Deploy':
            if lastReleaseIssue.deploymentTimeSelection is not None:
                timeDeltaToNextBuild, buildTime = BambooAdapter.findNextNamedBuildTime('prod', lastReleaseIssue.deploymentTimeSelection)
                return timeDeltaToNextBuild
            else:
                return None
        else:
            return None

    @property
    def lastTransitionDate(self):
        statusChangeDates = []
        for change in self.changelog:
            if change.get('item').get('field') == 'status':
                statusChangeDates.append(dateutil.parser.parse(change.get('changeDate')))

        if len(statusChangeDates) == 0:
            return None
        else:
            statusChangeDates.sort(reverse=True)
            return statusChangeDates[0]

    @staticmethod
    def getIssueJSON(issueNo):
        queryURL = jiraBaseURL + "issue/" + str(issueNo) + '?expand=changelog'
        jiraQueryResult = requests.get(queryURL, headers={'content-type': 'application/json', 'Accept': 'application/json'}, auth=(JIRA_USER, JIRA_PASS))
        issueJSON = json.loads(jiraQueryResult.text)
        logging.debug(issueJSON)
        return issueJSON

    @staticmethod
    def getIssueLinks(issueNo):
        issueJSON = Issue.getIssueJSON(issueNo)
        return Issue.getIssueLinksFromIssueJSON(issueJSON)

    @staticmethod
    def getIssueLinksFromIssueJSON(issueJSON):
        issueLinks = issueJSON.get('fields').get('issuelinks')
        linkedIssuesList = []
        for issueLink in issueLinks:
            inwardIssue = issueLink.get('inwardIssue')
            outwardIssue = issueLink.get('outwardIssue')
            linkedIssue = inwardIssue
            if linkedIssue is None:
                linkedIssue = outwardIssue
            issue = Issue.fromIssueJSON(linkedIssue)
            linkedIssuesList.append(issue)
        return linkedIssuesList

    @staticmethod
    def getIssueProjectKeyFromIssueNo(issueNo):
        return issueNo.split('-')[0]


def checkIssueState(req):
    result = req.get("result")
    parameters = result.get('parameters')

    if parameters is None:
        return {}

    issueNo = Common.getParameter(req, None, 'issueNo')
    issue = Issue.fromIssueNo(issueNo)
    speech = '%s is %s.' % (issue.key, issue.statusName)

    return Common.makeCommonResponse(speech)


def checkIssueDeploymentState(req):
    result = req.get("result")
    parameters = result.get('parameters')

    if parameters is None:
        return {}

    issueNo = Common.getParameter(req, None, 'issueNo')
    tense = Common.getParameter(req, None, 'tense')

    issue = Issue.fromIssueNo(issueNo)

    matchParameters = {'isDeployed': issue.isDeployed, 'tense': tense}

    message = Common.getMessageFromFile('outputs.yaml', 'checkIssueDeployment', matchParameters)

    deploymentDate = issue.deploymentDate
    if deploymentDate is not None:
        deploymentDate = Common.printDateTime(deploymentDate)

    message = Common.fillParameters({'issueNo': issue.key, 'deploymentDate': deploymentDate, 'nextDeploymentDate': Common.printTimeDelta(issue.timeToNextDeployment)}, message)

    speech = message

    return Common.makeCommonResponse(speech)
