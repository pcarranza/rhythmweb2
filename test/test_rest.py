import unittest
import json

from mock import Mock

from serve.rest.base import BaseRest
from serve.rest import JSon

from collections import defaultdict


class TestBaseRest(unittest.TestCase):

    def test_get_return_value_is_json(self):
        myjson = JSon()
        myjson.put('value', 1)
        stub = RestStub(Mock(), myjson)
        response = stub.do_get(defaultdict(Mock()), Mock())
        j = json.loads(response)
        self.assertEquals(1, j['value'])


    def test_post_return_value_is_json(self):
        components = defaultdict(Mock())
        myjson = JSon()
        myjson.put('value', 2)
        stub = RestStub(Mock(), myjson)
        response = stub.do_post(defaultdict(Mock()), Mock(), Mock())
        j = json.loads(response)
        self.assertEquals(2, j['value'])

    def test_error_404(self):
        components = defaultdict(Mock())
        stub = RestStub(Mock(), None)
        response = Mock()
        stub.do_get(defaultdict(Mock()), response)
        response.assert_called_with('404 NOT FOUND', 
                ('Content-type','text/html; charset=UTF-8'))



class RestStub(BaseRest):
    def __init__(self, components, reply_with):
        super(RestStub, self).__init__(components)
        self.reply_with = reply_with

    def get(self):
        return self.reply_with

    def post(self):
        return self.reply_with


