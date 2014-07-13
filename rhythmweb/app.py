import re
import os
import copy

from functools import partial
from collections import defaultdict

import logging
log = logging.getLogger(__name__)


class NoRouteError(Exception):
    pass


class App(object):

    def __init__(self):
        self.routes = {}
        self.file_groups = defaultdict(lambda: {})
        self.path_with_args_matcher = re.compile(r'(/.+?)<')
        self.args_matcher = re.compile(r'(<.*?>)')
        self.typed_rule_matcher = re.compile(r'<([\w\?]+):(int|float|str)>')
        self.simple_rule_matcher = re.compile(r'<([\w\?]+)>')

    def add_route(self, path, function):
        path, args = self.parse_route(path)
        self.routes[path] = (function, args)
        log.debug('Registering route {}'.format(path))

    def route(self, path, **kwargs):
        try:
            route, args = self.find_route(path)
            log.debug('Found route function {}'.format(route))
            return route(*args, **kwargs)
        except NoRouteError:
            return None

    def find_route(self, path):
        log.debug('Looking for route that matches {}'.format(path))
        possible = path.split('/')
        while possible:
            possible_path = '/'.join(possible)
            route, rules = self.routes.get(possible_path, (None, None))
            if route:
                log.debug('Found route {}'.format(possible_path))
                if rules:
                    rules = copy.copy(rules)
                    args = self.parse_path_args(path[len(possible_path):], rules)
                else:
                    args = []
                return route, args
            possible.pop()
        log.debug('Route for path {} not found'.format(path))
        raise NoRouteError()

    def parse_path_args(self, args, rules):
        log.debug('Looking for path arguments with this path {} and rules {}'.format(args, rules))
        slices = args.split('/')
        slices.reverse()
        rules.reverse()
        parsed_args = []
        while rules and slices:
            arg = slices.pop()
            if not arg:
                continue
            parsed_args.append(self.validate_rule(rules.pop(), arg))
        while rules:
            rule = rules.pop()
            log.debug('There are rules left: {}'.format(rule))
            if rule['optional']:
                parsed_args.append(None)
            else:
                raise NoRouteError()
        if slices:
            slices.reverse()
            log.debug('Path parts where not exausted, this is left: {}'.format(slices))
        return parsed_args

    def parse_rule(self, rule):
        typed_rule = self.typed_rule_matcher.match(rule)
        if typed_rule:
            name, kind = typed_rule.groups()
        else:
            name, kind = self.simple_rule_matcher.findall(rule)[0], 'str'
        optional = name.endswith('?')
        if optional:
            name = name[:-1]
        return {'name': name, 'type': kind, 'optional': optional}

    def validate_rule(self, rule, value):
        kind = rule['type']
        try:
            if kind == 'int':
                return int(value)
            elif kind == 'float':
                return float(value)
            else:
                return str(value)
        except:
            raise ValueError('{} is invalid as value for {}, {} expected'.format(value, rule['name'], kind))

    def parse_route(self, path):
        has_args = self.path_with_args_matcher.match(path)
        rules = []
        if has_args:
            args = self.args_matcher.findall(path)
            for arg in args:
                rules.append(self.parse_rule(arg))
            path = has_args.groups()[0]
        if path[-1] == '/':
            path = path[:-1]
        return path, rules

    def get_file(self, path, group):
        readfile = self.file_groups[group].get(path, None)
        if readfile:
            return readfile()
        return None

    def mount(self, path, group, ignore=None):
        if ignore_file(path):
            log.debug('Ignoring file {}'.format(path))
            return
        if os.path.isdir(path):
            for (dirpath, dirnames, filenames) in os.walk(path):
                log.debug('Walking dirpath {}'.format(dirpath))
                for filename in filenames:
                    self.mount(os.path.join(dirpath, filename), group, ignore)
                for dirname in dirnames:
                    log.debug('Mounting directory {} in path {}'.format(dirname, path))
                    self.mount(os.path.join(dirpath, dirname), group, ignore)
        elif os.path.isfile(path) or os.path.islink(path):
            route = '/{}'.format('/'.join(path.split('/')[1:]))
            if ignore and route.startswith(ignore):
                log.debug('Ignoring path start {}'.format(ignore))
                route = route[len(ignore):]
            log.debug('Registering route {} to read file {}'.format(route, path))
            self.file_groups[group][route] = partial(read_file, path)
        else:
            raise IOError('{} does not exists'.format(path))


def ignore_file(path):
    name = os.path.basename(path)
    if name.endswith('.py'):
        return True
    if name.endswith('.pyc'):
        return True
    if name.startswith('__') and name.endswith('__'):
        return True
    return False


def read_file(path):
    with open(path, 'rb') as f:
        return f.readlines()


def route(path):
    def decorate(func):
        app.add_route(path, func)
    return decorate


app = App()
