import unittest
import json

from serve.rest import JSon

class JsonTest(unittest.TestCase):

    def test_create_json_and_get_string(self):
        j = JSon()
        j.put('number', 1)
        j.put('string', 'some string')
        j.put('array', [2, 3])
        s = j.parse()
        parsed = json.loads(s)
        self.assertEquals(1, parsed['number'])
        self.assertEquals("some string", parsed['string'])
        self.assertEquals([2, 3], parsed['array'])
