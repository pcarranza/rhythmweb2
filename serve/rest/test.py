'''
Created on 14/12/2010

@author: jim
'''
import unittest
from serve.rest.json import JSon


class Test(unittest.TestCase):


    def testName(self):
        json = JSon('named_json')
        json.put('str_value', 'str')
        json.put('int_value', 1)
        
        
        jarray = []
        json1 = JSon()
        json1.put('array1', True);

        json2 = JSon()
        json2.put('array2', 111.2);
        
        jarray.append(json1)
        jarray.append(json2)
        
        json.put('jarray', jarray)
        
        print '-' + json.parse() + '-'


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
