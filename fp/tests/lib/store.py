# Import system modules
import os
import sys; sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
# Import custom modules
from libraries import store


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def testLoadQueue(self):
        # Set paths
        queuePath = 'testLoadQueue.queue'
        # Check that it works
        store.saveInformation(queuePath, {
            'parameters': {
                'int_parameter': 1,
                'float_parameter': 2.5,
            },
            'task1': {
                'string_parameter': 'string',
            },
        }, 'queue')
        expectedParameterByTaskByName = {
            'task1': {
                'int_parameter': 1,
                'float_parameter': 2.5,
                'string_parameter': 'string',
            },
        }
        actualParameterByTaskByName = store.loadQueue(queuePath, {
            'int_parameter': int, 
            'float_parameter': float, 
            'string_parameter': str,
        })
        self.assertEqual(expectedParameterByTaskByName, actualParameterByTaskByName)
        # Clean up
        os.remove(queuePath)


if __name__ == '__main__':
    unittest.main()
