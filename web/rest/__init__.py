import json
import logging

from serve.request import ServerException, ClientError

log = logging.getLogger(__name__)

HTML_HEADERS = [('Content-type','text/html; charset=UTF-8')]

class RBRest(object):

    def __init__(self):
        self.environment = None
        self.post_parameters = {}
        self.path_parameters = []

    def do_get(self, environ, response):
        self.environment = environ
        self.parse_path_parameters()
        try:
            return_value = self.get()
            log.debug('GET Method executed OK, sending ok response')
            return self.__return_ok(return_value, response)

        except ServerException as e:
            log.error('ServerException handling rest get', exc_info=True)
            response('%d %s' % (e.code, e.message), HTML_HEADERS)
            return e.message

        except Exception as e:
            log.error('Unknown exception when executing GET method: %s' % e, exc_info=True)
            response('%d %s' % (500, e), HTML_HEADERS)
            return '%d %s' % (500, e)

    def do_post(self, environ, post_params, response):
        self.post_parameters.update(post_params)
        self.environment = environ
        self.parse_path_parameters()

        log.debug("post parameters {}".format(post_params))
        try:
            return_value = self.post()
            log.debug('POST Method executed OK, sending ok response')
            return self.__return_ok(return_value, response)
        except ServerException as e:
            log.error('ServerException handling rest get', exc_info=True)
            response('%d %s' % (e.code, e.message), HTML_HEADERS)
            return e.message
        except Exception as e:
            log.error('Unknown exception when executing GET method: %s' % e, exc_info=True)
            response('%d %s' % (500, e), HTML_HEADERS)
            return '%d %s' % (500, e)

    def __return_ok(self, value, response):
        if value is None:
            return self.__do_page_not_found(response)

        if isinstance(value, dict):
            headers = []
            headers.append(('Content-type','application/json; charset=UTF-8'))
            headers.append(('Cache-Control: ', 'no-cache; must-revalidate'))
            response('200 OK', headers)
            return json.dumps(value)

        response('200 OK', HTML_HEADERS)
        return str(value)

    def parse_path_parameters(self):
        path_params = self.environment['PATH_PARAMS']
        if path_params:
            for param in [p for p in str(path_params).split('/') if p]:
                self.path_parameters.append(param)

    def __do_page_not_found(self, response):
        response('404 NOT FOUND', HTML_HEADERS)
        return self.__not_found()

    def __not_found(self):
        return 'Page not found'

    def get(self):
        raise ServerException(405, 'method GET not allowed')

    def post(self):
        raise ServerException(405, 'method POST not allowed')

    def unpack_value(self, value):
        if value is None:
            return None

        if type(value) is dict:
            log.debug('Value is as dictionary, returning dictionary')
            return value

        elif type(value) is list:
            if len(value) == 1:
                log.debug('Value was packed as 1 element list')
                svalue = value[0]
                if type(svalue) is str:
                    svalue = svalue.strip()
                    log.debug('Value "%s" is a string, returning stripped' % svalue)
                else:
                    log.debug('Value has type "%s", returning value' % type(svalue))
                return svalue
            else:
                log.debug('Value is a list of %d elements, returning list' % len(value))
                return value
        else:
            log.debug('Value has type "%s", returning value' % type(value))
            return value

    def get_path_parameters(self):
        return self.path_parameters

    def has_parameter(self, key):
        if not self.post_parameters:
            return False
        return key in self.post_parameters

    def get_parameter(self, key, required=False):
        try:
            param = self.post_parameters.get(key, None)
            if required and param is None:
                raise ClientError('no "{}" parameter'.format(key))
            return self.unpack_value(param)
        except ClientError:
            raise
        except:
            raise ServerException(500, 'Could not unpack post parameter {}'.format(key))

    def has_post_parameters(self):
        if self.post_parameters is None:
            return False

        if not self.post_parameters:
            return False

        if len(self.post_parameters) == 0:
            return False

        return True

    def has_path_parameters(self):
        if not self.path_parameters:
            return False
        return True

    def get_parameters_size(self):
        return 0 if not self.post_parameters else len(self.post_parameters)

    def get_path_parameters_size(self):
        return 0 if not self.path_parameters else len(self.path_parameters)

    def get_path_parameter(self, index):
        if not self.path_parameters:
            return None
        try:
            return self.unpack_value(self.path_parameters[index])
        except IndexError:
            log.warn('No path param with index %d' % index)
            return None
        except:
            raise ServerException(500, 'Could not unpack path parameter %d' % index)

    def to_int(self, value, message='value must be a number'):
        return self.cast(value, message, int)

    def to_float(self, value, message='value must be a number'):
        return self.cast(value, message, float)

    def cast(self, value, message, func):
        if value is None:
            return None
        try:
            return func(value)
        except:
            log.error('Cannot cast "{}": {}'.format(value, message))
            raise ServerException(400, 'Bad Request: {}'.format(message))

