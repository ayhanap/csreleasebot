# -*- coding: utf-8 -*-
import logging
import unittest

import dateutil.parser

from csreleasebot import JiraAdapter
from csreleasebot.JiraAdapter import Issue

logger = logging.getLogger()
logger.level = logging.DEBUG


class TestJiraAdapter(unittest.TestCase):

    def testGetIssueJSON(self):
        issueNo = 'CDBT-4289'
        issueJSON = Issue.getIssueJSON(issueNo)
        self.assertEqual(issueJSON.get('key'), issueNo)

    def testGetIssueLinks(self):
        issueNo = 'CDBT-4289'
        issueLinks = Issue.getIssueLinks(issueNo)
        for issueLink in issueLinks:
            self.assertTrue(issueLink.key in ['CDBR-879', 'CDBR-882', 'CDBR-884', 'CDBR-888', 'CDBR-897', 'CDBR-898'])

    def testGetIssue(self):
        issueNo = 'CDBT-4289'
        issue = Issue.fromIssueNo(issueNo)
        self.assertEqual(issue.key, issueNo)
        self.assertEqual(issue.id, '46601')
        self.assertEqual(issue.statusName, 'Closed')
        self.assertEqual(issue.statusCategoryId, 3)

    def testGetIssueProjectKeyFromIssueNo(self):
        issueProjectKey = Issue.getIssueProjectKeyFromIssueNo('CDBT-4289')
        self.assertEqual(issueProjectKey, 'CDBT')

    def testFindLastRelease(self):
        issueNo = 'CDBT-4289'
        issue = Issue.fromIssueNo(issueNo)
        lastReleaseIssue = issue.getLastReleaseIssue()
        self.assertEqual(lastReleaseIssue.key, 'CDBR-898')

    def testFindLastReleaseEmpty(self):
        issueNo = 'CDBT-4288'
        issue = Issue.fromIssueNo(issueNo)
        lastReleaseIssue = issue.getLastReleaseIssue()
        self.assertIsNone(lastReleaseIssue)

    def testGetIssueResolutionDate(self):
        issueNo = 'CDBT-4289'
        issue = Issue.fromIssueNo(issueNo)
        self.assertEqual(issue.resolutionDate, dateutil.parser.parse('2016-12-16T14:57:35.687+0200'))
        lastReleaseIssue = issue.getLastReleaseIssue()
        print(lastReleaseIssue.resolutionDate)
        self.assertIsNotNone(lastReleaseIssue.resolutionDate)

    def testCheckIfIssueDeployed(self):
        issueNo = 'CDBT-4289'
        issue = Issue.fromIssueNo(issueNo)
        self.assertTrue(issue.isDeployed)

    def testCheckIfIssueNotDeployed(self):
        issueNo = 'CDB-1089'
        issue = Issue.fromIssueNo(issueNo)
        self.assertFalse(issue.isDeployed)

    def testGetDeploymentDate(self):
        issueNo = 'CDBT-4289'
        issue = Issue.fromIssueNo(issueNo)
        self.assertEqual(issue.deploymentDate, dateutil.parser.parse('2016-12-26T15:21:55.097+0200'))

    def testGetLastTransitionDate(self):
        issueNo = 'CDBR-909'
        issue = Issue.fromIssueNo(issueNo)
        self.assertEqual(issue.lastTransitionDate, dateutil.parser.parse('2016-12-28T19:01:00.959+0200'))

    def testGetNextDeploymentDate(self):
        # <editor-fold desc="issueJSON">
        issueJSON = {
            "expand": "renderedFields,names,schema,transitions,operations,editmeta,changelog",
            "id": "48001",
            "self": "http://issues.orioncb.com/rest/api/2/issue/48001",
            "key": "CDBR-915",
            "fields": {
                "issuetype": {
                    "self": "http://issues.orioncb.com/rest/api/2/issuetype/10200",
                    "id": "10200",
                    "description": "",
                    "iconUrl": "http://issues.orioncb.com/secure/viewavatar?size=xsmall&avatarId=11600&avatarType=issuetype",
                    "name": "Release",
                    "subtask": False,
                    "avatarId": 11600
                },
                "components": [
                    {
                        "self": "http://issues.orioncb.com/rest/api/2/component/11300",
                        "id": "11300",
                        "name": "RLM"
                    }
                ],
                "timespent": None,
                "timeoriginalestimate": None,
                "description": "Bu talep,Utility projesinin PROD branch'inin [74|http://build.orioncb.com/browse/beta] nolu build'inden oluşturulan ürünlerin CDB ortamına çıkması için otomatik olarak oluşturulmuştur.\n[deploymentLogs|http://build.orioncb.com/deploy/viewDeploymentResult.action?deploymentResultId=258342914]",
                "project": {
                    "self": "http://issues.orioncb.com/rest/api/2/project/10200",
                    "id": "10200",
                    "key": "CDBR",
                    "name": "(Release) Caspian Development Bank",
                    "avatarUrls": {
                        "48x48": "http://issues.orioncb.com/secure/projectavatar?pid=10200&avatarId=11601",
                        "24x24": "http://issues.orioncb.com/secure/projectavatar?size=small&pid=10200&avatarId=11601",
                        "16x16": "http://issues.orioncb.com/secure/projectavatar?size=xsmall&pid=10200&avatarId=11601",
                        "32x32": "http://issues.orioncb.com/secure/projectavatar?size=medium&pid=10200&avatarId=11601"
                    }
                },
                "customfield_10010": None,
                "customfield_10011": None,
                "fixVersions": [],
                "aggregatetimespent": None,
                "resolution": None,
                "timetracking": {},
                "customfield_10500": {
                    "self": "http://issues.orioncb.com/rest/api/2/customFieldOption/10301",
                    "value": "Akşam",
                    "id": "10301"
                },
                "customfield_10402": "beta-74",
                "customfield_10403": "74",
                "attachment": [],
                "customfield_10405": None,
                "aggregatetimeestimate": None,
                "resolutiondate": None,
                "workratio": -1,
                "summary": "Utility Sürüm Talebi beta-74",
                "lastViewed": "2017-01-02T12:22:36.686+0200",
                "watches": {
                    "self": "http://issues.orioncb.com/rest/api/2/issue/CDBR-915/watchers",
                    "watchCount": 1,
                    "isWatching": False
                },
                "creator": {
                    "self": "http://issues.orioncb.com/rest/api/2/user?username=jupiter",
                    "name": "jupiter",
                    "key": "jupiter",
                    "emailAddress": "ayhan.apaydin@cs.com.tr",
                    "avatarUrls": {
                        "48x48": "http://issues.orioncb.com/secure/useravatar?ownerId=jupiter&avatarId=11801",
                        "24x24": "http://issues.orioncb.com/secure/useravatar?size=small&ownerId=jupiter&avatarId=11801",
                        "16x16": "http://issues.orioncb.com/secure/useravatar?size=xsmall&ownerId=jupiter&avatarId=11801",
                        "32x32": "http://issues.orioncb.com/secure/useravatar?size=medium&ownerId=jupiter&avatarId=11801"
                    },
                    "displayName": "jupiter",
                    "active": True,
                    "timeZone": "Europe/Istanbul"
                },
                "subtasks": [],
                "created": "2017-01-02T12:22:14.270+0200",
                "reporter": {
                    "self": "http://issues.orioncb.com/rest/api/2/user?username=jupiter",
                    "name": "jupiter",
                    "key": "jupiter",
                    "emailAddress": "ayhan.apaydin@cs.com.tr",
                    "avatarUrls": {
                        "48x48": "http://issues.orioncb.com/secure/useravatar?ownerId=jupiter&avatarId=11801",
                        "24x24": "http://issues.orioncb.com/secure/useravatar?size=small&ownerId=jupiter&avatarId=11801",
                        "16x16": "http://issues.orioncb.com/secure/useravatar?size=xsmall&ownerId=jupiter&avatarId=11801",
                        "32x32": "http://issues.orioncb.com/secure/useravatar?size=medium&ownerId=jupiter&avatarId=11801"
                    },
                    "displayName": "jupiter",
                    "active": True,
                    "timeZone": "Europe/Istanbul"
                },
                "customfield_10000": None,
                "aggregateprogress": {
                    "progress": 0,
                    "total": 0
                },
                "priority": {
                    "self": "http://issues.orioncb.com/rest/api/2/priority/2",
                    "iconUrl": "http://issues.orioncb.com/images/icons/priorities/high.png",
                    "name": "High",
                    "id": "2"
                },
                "customfield_10002": None,
                "customfield_10300": "Utility-74.zip",
                "labels": [],
                "customfield_10400": "Infrastructure - Utility - beta",
                "environment": None,
                "timeestimate": None,
                "aggregatetimeoriginalestimate": None,
                "versions": [],
                "duedate": None,
                "progress": {
                    "progress": 0,
                    "total": 0
                },
                "issuelinks": [],
                "comment": {
                    "startAt": 0,
                    "maxResults": 0,
                    "total": 0,
                    "comments": []
                },
                "worklog": {
                    "startAt": 0,
                    "maxResults": 20,
                    "total": 0,
                    "worklogs": []
                },
                "assignee": {
                    "self": "http://issues.orioncb.com/rest/api/2/user?username=ayhan.apaydin",
                    "name": "ayhan.apaydin",
                    "key": "ayhan.apaydin",
                    "emailAddress": "ayhan.apaydin@cybersoft.com.tr",
                    "avatarUrls": {
                        "48x48": "http://issues.orioncb.com/secure/useravatar?ownerId=ayhan.apaydin&avatarId=10405",
                        "24x24": "http://issues.orioncb.com/secure/useravatar?size=small&ownerId=ayhan.apaydin&avatarId=10405",
                        "16x16": "http://issues.orioncb.com/secure/useravatar?size=xsmall&ownerId=ayhan.apaydin&avatarId=10405",
                        "32x32": "http://issues.orioncb.com/secure/useravatar?size=medium&ownerId=ayhan.apaydin&avatarId=10405"
                    },
                    "displayName": "Ayhan Apaydın",
                    "active": True,
                    "timeZone": "Europe/Istanbul"
                },
                "updated": "2017-01-02T12:22:36.464+0200",
                "status": {
                    "self": "http://issues.orioncb.com/rest/api/2/status/10201",
                    "description": "Deploy olmak için sürüm saatini bekliyor.",
                    "iconUrl": "http://issues.orioncb.com/images/icons/statuses/generic.png",
                    "name": "Ready To Deploy",
                    "id": "10201",
                    "statusCategory": {
                        "self": "http://issues.orioncb.com/rest/api/2/statuscategory/4",
                        "id": 4,
                        "key": "indeterminate",
                        "colorName": "yellow",
                        "name": "In Progress"
                    }
                }
            },
            "changelog": {
                "startAt": 0,
                "maxResults": 1,
                "total": 1,
                "histories": [
                    {
                        "id": "90503",
                        "author": {
                            "self": "http://issues.orioncb.com/rest/api/2/user?username=ayhan.apaydin",
                            "name": "ayhan.apaydin",
                            "key": "ayhan.apaydin",
                            "emailAddress": "ayhan.apaydin@cybersoft.com.tr",
                            "avatarUrls": {
                                "48x48": "http://issues.orioncb.com/secure/useravatar?ownerId=ayhan.apaydin&avatarId=10405",
                                "24x24": "http://issues.orioncb.com/secure/useravatar?size=small&ownerId=ayhan.apaydin&avatarId=10405",
                                "16x16": "http://issues.orioncb.com/secure/useravatar?size=xsmall&ownerId=ayhan.apaydin&avatarId=10405",
                                "32x32": "http://issues.orioncb.com/secure/useravatar?size=medium&ownerId=ayhan.apaydin&avatarId=10405"
                            },
                            "displayName": "Ayhan Apaydın",
                            "active": True,
                            "timeZone": "Europe/Istanbul"
                        },
                        "created": "2017-01-02T12:22:36.468+0200",
                        "items": [
                            {
                                "field": "Deployment Time",
                                "fieldtype": "custom",
                                "from": None,
                                "fromString": None,
                                "to": "10301",
                                "toString": "Akşam"
                            },
                            {
                                "field": "status",
                                "fieldtype": "jira",
                                "from": "10200",
                                "fromString": "Deployment Configuration",
                                "to": "10201",
                                "toString": "Ready To Deploy"
                            }
                        ]
                    }
                ]
            }
        }
        # </editor-fold>
        issue = Issue.fromIssueJSON(issueJSON)
        #self.assertEqual(issue.timeToNextDeployment, dateutil.parser.parse('2017-01-02T12:00:00.000+0300'))

    def testCheckIssueStateIntent(self):
        # <editor-fold desc="req">
        req = {
            "id": "90093be8-c965-4a84-8b00-df771fcd7710",
            "timestamp": "2016-12-29T11:05:58.477Z",
            "result": {
                "source": "agent",
                "resolvedQuery": "what is the status of CDBT-4289?",
                "action": "check-issue-state",
                "actionIncomplete": 'False',
                "parameters": {
                    "issueNo": "CDBT-4289"
                },
                "contexts": [],
                "metadata": {
                    "intentId": "f96b6614-50fd-4f03-8c3c-f254b6956b67",
                    "webhookUsed": "False",
                    "webhookForSlotFillingUsed": "False",
                    "intentName": "Issue-check-state"
                },
                "fulfillment": {
                    "speech": "I don't know CDBT-4289",
                    "messages": [
                        {
                            "type": 0,
                            "speech": "I don't know CDBT-4289"
                        }
                    ]
                },
                "score": 0.92
            },
            "status": {
                "code": 200,
                "errorType": "success"
            },
            "sessionId": "b384a12d-9034-48d4-8b1c-85edb776fd72"
        }
        # </editor-fold>
        resultJSON = JiraAdapter.checkIssueState(req)
        speech = resultJSON.get('speech')
        self.assertEqual(speech, "CDBT-4289 is Closed.")

    def testCheckIssueDeploymentIntent(self):
        # <editor-fold desc="req">
        req = {
            "id": "479382fa-3943-4e6b-a813-2c1e1fe7f0c7",
            "timestamp": "2016-12-29T11:28:25.994Z",
            "result": {
                "source": "agent",
                "resolvedQuery": "when will CDBT-4289 deploy?",
                "action": "",
                "actionIncomplete": 'False',
                "parameters": {
                    "issueNo": "CDBT-4289",
                    "tense": "future"
                },
                "contexts": [],
                "metadata": {
                    "intentId": "ff482890-da5b-4f3a-90e3-695ef34f8af4",
                    "webhookUsed": "True",
                    "webhookForSlotFillingUsed": "False",
                    "intentName": "Issue-check-deployment"
                },
                "fulfillment": {
                    "messages": [
                        {
                            "type": 0,
                            "speech": ""
                        }
                    ]
                },
                "score": 1
            },
            "status": {
                "code": 200,
                "errorType": "success"
            },
            "sessionId": "b384a12d-9034-48d4-8b1c-85edb776fd72"
        }
        # </editor-fold>
        resultJSON = JiraAdapter.checkIssueDeploymentState(req)
        speech = resultJSON.get('speech')
        self.assertEqual(speech, 'CDBT-4289 is already Deployed at 26 December 2016 15:21:55.')


if __name__ == '__main__':
    unittest.main()
