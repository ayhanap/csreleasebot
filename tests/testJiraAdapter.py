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
        print lastReleaseIssue.resolutionDate
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

    def testCheckIssueStateIntent(self):
        req = {
            "id": "90093be8-c965-4a84-8b00-df771fcd7710",
            "timestamp": "2016-12-29T11:05:58.477Z",
            "result": {
                "source": "agent",
                "resolvedQuery": "what is the status of CDBT-4289?",
                "action": "check-issue-state",
                "actionIncomplete": 'false',
                "parameters": {
                    "issueNo": "CDBT-4289"
                },
                "contexts": [],
                "metadata": {
                    "intentId": "f96b6614-50fd-4f03-8c3c-f254b6956b67",
                    "webhookUsed": "false",
                    "webhookForSlotFillingUsed": "false",
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
        resultJSON = JiraAdapter.checkIssueState(req)
        speech = resultJSON.get('speech')
        self.assertEqual(speech, "CDBT-4289 is Closed.")

    def testCheckIssueDeploymentIntent(self):
        req = {
            "id": "479382fa-3943-4e6b-a813-2c1e1fe7f0c7",
            "timestamp": "2016-12-29T11:28:25.994Z",
            "result": {
                "source": "agent",
                "resolvedQuery": "when will CDBT-4289 deploy?",
                "action": "",
                "actionIncomplete": 'false',
                "parameters": {
                    "issueNo": "CDBT-4289",
                    "tense": "future"
                },
                "contexts": [],
                "metadata": {
                    "intentId": "ff482890-da5b-4f3a-90e3-695ef34f8af4",
                    "webhookUsed": "true",
                    "webhookForSlotFillingUsed": "false",
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
        resultJSON = JiraAdapter.checkIssueDeploymentState(req)
        speech = resultJSON.get('speech')
        self.assertEqual(speech, "CDBT-4289 is already Deployed.")


if __name__ == '__main__':
    unittest.main()
