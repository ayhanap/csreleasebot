import json
import os

import logging

import dateutil.parser
import requests

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
        return issue

    # fills sub variables if didnt exist at the creation
    def __getattribute__(self, name):
        if not super(Issue, self).__getattribute__('isInit'):
            val = super(Issue, self).__getattribute__(name)
            if val is None:
                self.__dict__.update(self.fromIssueNo(self.key).__dict__)
                print "INIT!"
                return super(Issue, self).__getattribute__(name)
            return val
        return super(Issue, self).__getattribute__(name)

    def getLastReleaseIssue(self):
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

    @staticmethod
    def getIssueJSON(issueNo):
        queryURL = jiraBaseURL + "issue/" + str(issueNo)
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
