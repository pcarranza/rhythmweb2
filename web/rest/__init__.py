import json
import logging

from serve.request import ServerException

log = logging.getLogger(__name__)

HTML_HEADERS = [('Content-type','text/html; charset=UTF-8')]

class RBRest(object):

    def __init__(self, components):
        self._components = components
        self.__parameters = None
        self.__environ = None

    def do_get(self, environ, response):
        self.__environ = environ
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
        self.__parameters = post_params
        self.__environ = environ
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
        path_params = self.__environ['PATH_PARAMS']

        querystring_params = []
        if path_params:
            params = str(path_params).split('/')
            for param in params:
                if param:
                    querystring_params.append(param)

        self.__path_params = querystring_params

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

    def pack_as_list(self, value):
        if type(value) is list:
            return value
        elif type(value) is dict:
            return_value = []
            for v in value:
                return_value.append(value[v])
            return return_value
        elif type(value) is str and ',' in value:
            return value.split(',')
        else:
            return [value]

    def get_environment(self):
        return self.__environ

    def get_parameters(self):
        return self.__parameters

    def get_path_parameters(self):
        return self.__path_params

    def has_parameter(self, key):
        if not self.__parameters:
            return False

        return key in self.__parameters

    def get_parameter(self, key, required=False):
        if not self.has_parameter(key):
            if required:
                raise ServerException(400, 'Bad request, no "%s" parameter' % key)
            else:
                return None

        try:
            param = self.__parameters[key]
            param = self.unpack_value(param)
            return param
        except:
            raise ServerException(500, 'Could not unpack post parameter %d' % key)

    def has_post_parameters(self):
        if self.__parameters is None:
            return False

        if not self.__parameters:
            return False

        if len(self.__parameters) == 0:
            return False

        return True

    def has_path_parameters(self):
        if self.__path_params is None:
            return False

        if not self.__path_params:
            return False

        if len(self.__path_params) == 0:
            return False
        return True

    def get_parameters_size(self):
        if not self.__parameters:
            return 0

        return len(self.__parameters)

    def get_path_parameters_size(self):
        if not self.__path_params:
            return 0

        return len(self.__path_params)

    def get_path_parameter(self, index):
        if not self.__path_params:
            log.warn('No path param with index %d (empty path params)' % index)
            return None

        if self.get_path_parameters_size() < index + 1:
            log.warn('No path param with index %d' % index)
            return None

        try:
            param = self.__path_params[index]
            param = self.unpack_value(param)
            return param
        except:
            raise ServerException(500, 'Could not unpack path parameter %d' % index)

    def get_rb_handler(self):
        return self._components.get('RB', None)
