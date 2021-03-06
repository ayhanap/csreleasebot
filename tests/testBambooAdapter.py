# -*- coding: utf-8 -*-
import logging
import unittest


from csreleasebot import BambooAdapter

logger = logging.getLogger()
logger.level = logging.DEBUG


class TestBambooAdapter(unittest.TestCase):

    def testGetBuildResult(self):
        buildResultJSON = BambooAdapter.getBuildResult('ibank', 'latest')
        self.assertNotEqual(buildResultJSON.get('planName'), None)

    def testBambooReleaseResult(self):
        build = BambooAdapter.findSingleBuildState("ibank", "1527")
        print(build.buildNumber, build.buildState)
        self.assertEqual(build.buildNumber, 1527)
        self.assertEqual(build.buildState, "Successful")

    def testBambooReleaseResultOneParam(self):
        build = BambooAdapter.findSingleBuildState("ibank", None)
        print(build.buildNumber, build.buildState)
        self.assertEqual(build.buildState, "Successful")

    def testFindNextBuildTime(self):
        timeToNextBuildVar, buildTime = BambooAdapter.findNextBuildTime('prod')
        print(str(timeToNextBuildVar))
        print(buildTime)

    def testFindNextNamedBuildTime(self):
        timeToNextBuildVar, buildTime = BambooAdapter.findNextNamedBuildTime('prod', 'Öğlen')
        print(timeToNextBuildVar)
        self.assertEqual(str(buildTime), '12:00:00')


if __name__ == '__main__':
    unittest.main()