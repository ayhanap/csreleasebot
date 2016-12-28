import logging
import unittest
import yaml

from csreleasebot import BambooAdapter
from csreleasebot import Common
from csreleasebot import app

logger = logging.getLogger()
logger.level = logging.DEBUG


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def testBambooReleaseResult(self):
        build = BambooAdapter.findSingleBuildState("ibank", "1527")
        print build.buildNumber, build.buildState
        self.assertEqual(build.buildNumber, 1527)
        self.assertEqual(build.buildState, "Successful")

    def testBambooReleaseResultOneParam(self):
        build = BambooAdapter.findSingleBuildState("ibank", None)
        print build.buildNumber, build.buildState
        self.assertEqual(build.buildState, "Successful")

    def testFindNextBuildTime(self):
        BambooAdapter.findNextBuildTime('beta')

    def testGetModelFromFile(self):
        parameters = {'releaseState': 'running', 'tense': 'past', 'buildResult': BambooAdapter.BuildState.COMPLETE.value}
        message = Common.getMessageFromFile('csreleasebot/outputs.yaml', 'checkTimeResults', parameters)
        self.assertEqual(message, '{releaseName} release is completed {build.buildRelativeTime}.')

    def testGetModelFromFile2(self):
        parameters = {'tense': 'past', 'currentBuildState': BambooAdapter.BuildState.RUNNING.value}
        message = Common.getMessageFromFile('csreleasebot/outputs.yaml', 'checkTimeResults', parameters)
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


if __name__ == '__main__':
    unittest.main()