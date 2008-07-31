from imgserver.tempfilecreationstrategy import createTempFileStrategy
import unittest
import os

class TempFileCreationStrategyTestCase(unittest.TestCase):
    
    def testShouldCreateAndRemoveTempFile(self):
        strategy = createTempFileStrategy()
        tf = strategy.createTempFile()
        filename = tf.name
        self.assertTrue(os.path.exists(filename))
        strategy.deleteTempFile(tf)
        # force garbage collection
        tf = None
        self.assertFalse(os.path.exists(filename))
        