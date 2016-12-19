import unittest
import app
import logging

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
        buildNumber, buildState = app.findBuildState("ibank","1527")
        print buildNumber, buildState
        self.assertEqual(buildNumber, 1527)
        self.assertEqual(buildState, "Successful")

    def testBambooReleaseResultOneParam(self):
        buildNumber, buildState = app.findBuildState("ibank",None)
        print buildNumber, buildState
        self.assertEqual(buildState, "Successful")

if __name__ == '__main__':
    unittest.main()