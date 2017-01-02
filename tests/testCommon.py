import unittest
import datetime as dt

import dateutil.parser

from csreleasebot import BambooAdapter
from csreleasebot import Common


class TestCommon(unittest.TestCase):

    def testGetModelFromFile(self):
        parameters = {'releaseState': 'running', 'tense': 'past', 'buildResult': BambooAdapter.BuildState.COMPLETE.value}
        message = Common.getMessageFromFile('outputs.yaml', 'checkReleaseTime', parameters)
        self.assertEqual(message, '{releaseName} release is completed {build.buildRelativeTime}.')

    def testGetModelFromFile2(self):
        parameters = {'tense': 'past', 'currentBuildState': BambooAdapter.BuildState.RUNNING.value}
        message = Common.getMessageFromFile('outputs.yaml', 'checkReleaseTime', parameters)
        self.assertEqual(message, '{releaseName} will be completed in {build.prettyTimeRemaining}.')

    def testParameterExtraction(self):
        matches = Common.extractParametersFromText('{hello} beautiful {world} tell me {some.Joke}')
        self.assertEqual(matches, ['hello', 'world', 'some.Joke'])

    def testParameterFilling(self):
        build = BambooAdapter.Build()
        build.lifeCycleState = 'Running'
        build.buildRelativeTime = '12:00:00'
        valuesToFill = {'build': build, 'releaseName': 'prod'}
        filledString = Common.fillParameters(valuesToFill, '{releaseName} release is completed at {build.buildRelativeTime}.')
        self.assertEqual(filledString, 'prod release is completed at 12:00:00.')

    def testParameterFillingWithMethodPassing(self):
        def timeToNextBuild(values):
            releaseName = values.get('releaseName')
            if releaseName == 'prod':
                return '3:11:00'
            else:
                return '2:00:00'

        valuesToFill = {'releaseName': 'prod', 'timeToNextBuild': timeToNextBuild}
        filledString = Common.fillParameters(valuesToFill, '{releaseName} release will start in {timeToNextBuild} hours.')
        self.assertEqual(filledString, 'prod release will start in 3:11:00 hours.')

    def testPrintTimeDelta(self):
        timeDelta = dt.timedelta(hours=12, minutes=35, seconds=23)
        timeDeltaStr = Common.printTimeDelta(timeDelta)
        self.assertEqual(timeDeltaStr, "12 hours, 35 minutes, 23 seconds later")

        timeDeltaBefore = dt.timedelta(hours=-12, minutes=35, seconds=23)
        timeDeltaBeforeStr = Common.printTimeDelta(timeDeltaBefore)
        self.assertEqual(timeDeltaBeforeStr, "12 hours, 35 minutes, 23 seconds ago")

        timeDeltaBefore = dt.timedelta(minutes=35, seconds=23)
        timeDeltaBeforeStr = Common.printTimeDelta(timeDeltaBefore)
        self.assertEqual(timeDeltaBeforeStr, "35 minutes, 23 seconds later")

    def testPrintDatetime(self):
        datetime = dateutil.parser.parse('2017-01-02T12:22:36.686+0200')
        datetimeText = Common.printDateTime(datetime)
        self.assertEqual(datetimeText, '02 January 2017 13:22:36')


if __name__ == '__main__':
    unittest.main()
