import unittest
import json

from mock import Mock

from web.rest import RBRest
from serve.request import ServerException

from collections import defaultdict


class TestRBRest(unittest.TestCase):

    def test_get_return_value_is_json(self):
        myjson = {}
        myjson['value'] = 1
        stub = RestStub(Mock(), myjson)
        response = stub.do_get(defaultdict(Mock()), Mock())
        j = json.loads(response)
        self.assertEquals(1, j['value'])


    def test_post_return_value_is_json(self):
        myjson = {}
        myjson['value'] = 2
        stub = RestStub(Mock(), myjson)
        response = stub.do_post(defaultdict(Mock()), Mock(), Mock())
        j = json.loads(response)
        self.assertEquals(2, j['value'])

    def test_error_404(self):
        stub = RestStub(Mock(), None)
        response = Mock()
        stub.do_get(defaultdict(Mock()), response)
        response.assert_called_with('404 NOT FOUND', 
                [('Content-type','text/html; charset=UTF-8')])

    def test_parse_path(self):
        environment = defaultdict(Mock())
        environment['PATH_PARAMS'] = 'bla/final'
        stub = RestStub(Mock(), 'response')
        response = stub.do_get(environment, Mock())
        params = stub.get_path_parameters()
        self.assertEquals(['bla', 'final'], params)
        self.assertEquals('response', response)

    def test_ServerException_on_get(self):
        stub = RestStub(Mock(), None)
        stub.get = Mock()
        stub.get.side_effect = ServerException(500, 'my mistake')
        response = Mock()
        stub.do_get(defaultdict(Mock()), response)
        response.assert_called_with('500 my mistake', 
                [('Content-type', 'text/html; charset=UTF-8')])






class RestStub(RBRest):
    def __init__(self, components, reply_with):
        super(RestStub, self).__init__(components)
        self.reply_with = reply_with

    def get(self):
        return self.reply_with

    def post(self):
        return self.reply_with


