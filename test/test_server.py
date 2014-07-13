
import unittest

from mock import Mock, patch
from io import BytesIO
from rhythmweb.server import Server
from rhythmweb.app import app, route


@patch('rhythmweb.server.Response')
class TestNewServer(unittest.TestCase):

    def test_get_index_file(self, response_class):
        server = Server()
        response = Mock()
        response_class.return_value = response
        server.handle_request({}, Mock())
        content = app.get_file('/index.html', 'default')
        self.assertIsNotNone(content)
        response.reply_with_file.assert_called_with('/index.html',content)

    def test_file_not_found(self, response_class):
        server = Server()
        response = Mock()
        response_class.return_value = response
        server.handle_request({'PATH_INFO': '/index.py'}, Mock())
        response.reply_with_not_found.assert_called_with()

    def test_return_dict_with_path_argument(self, response_class):
        server = Server()
        response = Mock()
        response_class.return_value = response
        server.handle_request({'PATH_INFO': '/something/myarg'}, Mock())
        response.reply_with_json.assert_called_with({'the_argument': 'myarg'})

    def test_post_plain_parameters(self, response_class):
        server = Server()
        response = Mock()
        response_class.return_value = response
        server.handle_request(
            {
                'PATH_INFO': '/path/with/kwargs',
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'wsgi.input': BytesIO(b'key1=value1&key2=value2')
            }, Mock())
        response.reply_with_json.assert_called_with({
            'key1': 'value1',
            'key2': 'value2'})

    def test_post_list_parameters(self, response_class):
        server = Server()
        response = Mock()
        response_class.return_value = response
        server.handle_request(
            {
                'PATH_INFO': '/path/with/kwargs',
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'wsgi.input': BytesIO(b'key1=value1,value3,value5')
            }, Mock())
        response.reply_with_json.assert_called_with({
            'key1': 'value1,value3,value5'})



@route('/something/<argument>')
def try_one_path_argument(argument):
    return {'the_argument': argument}

@route('/path/with/kwargs')
def path_with_kwargs(**kwargs):
    return kwargs
