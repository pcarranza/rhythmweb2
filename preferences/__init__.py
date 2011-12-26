# -*- coding: utf-8 -
# Rhythmweb - Rhythmbox web REST + Ajax environment for remote control
# Copyright (C) 2010  Pablo Carranza
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import os
import gobject
from serve.log import LOG_LEVEL_ARRAY
from serve.log.loggable import Loggable


class Preferences(Loggable):
    
    ui_file = ''
    button = None
    config = None
    
    def __init__(self, config, config_path):
        path = os.path.dirname(__file__)
        path = os.path.join(path, 'preferences.glade')
        self.ui_file = path
        self.config = config
        self.config_path = config_path
        
    
    def show_dialog(self):
        builder = gtk.Builder()
        builder.add_from_file(self.ui_file)
        window = builder.get_object("ConfigWindow")
        window.connect("delete-event", lambda x: self.save(builder) )
        builder.get_object("close_button").connect('clicked', lambda x: self.save(builder) )
        self.button = builder.get_object("close_button")
        self.load_config(builder)
        window.show_all()
        return window
    
    
    def __add_combobox_model(self, combo):
        model = gtk.ListStore(gobject.TYPE_STRING)
        combo.set_model(model)
    
    
    def __add_cell_renderer(self, combo):
        cell_renderer = gtk.CellRendererText()
        combo.pack_start(cell_renderer, True)
        combo.add_attribute(cell_renderer, 'text', 0)
    
    
    def __setup_combobox(self, combo):
        self.__add_combobox_model(combo)
        self.__add_cell_renderer(combo)
    
    
    def __load_themes(self, combo, key):
        selected_theme = self.config.get_string(key, False, 'default')
        resources = self.config.get_string('*resources')
        
        self.trace('Listing resources at %s' % resources)
        dirs = os.listdir(resources)
        
        index = 0
        for dir in dirs:
            if os.path.isdir(os.path.join(resources, dir)):
                combo.append_text(dir)
                if dir == selected_theme:
                    combo.set_active(index)
                    self.debug('Selecting %s' % dir)
                index += 1
    
    
    def __load_debug_level(self, combo):
        selected_level= self.config.get_string('log.level', True, 'INFO')
        index = 0
        for key in LOG_LEVEL_ARRAY:
            combo.append_text(key)
            if key == selected_level:
                combo.set_active(index)
            index += 1
    
    
    def __load_proxy(self, proxy_enabled, hostname, port):
        is_enabled = self.config.get_boolean('proxy', False, False)
        proxy_hostname = self.config.get_string('proxy.hostname', False, '127.0.0.1')
        proxy_port = self.config.get_string('proxy.port', False, '7000')
        
        proxy_enabled.set_active(is_enabled)
        hostname.set_text(proxy_hostname)
        port.set_text(proxy_port)
    
    
    def __load_networking(self, hostname, port):
        _hostname = self.config.get_string('hostname', False, '127.0.0.1')
        _port = self.config.get_string('port', False, '7001')
        
        hostname.set_text(_hostname)
        port.set_text(_port)
        
    
    def load_config(self, builder):
        theme = builder.get_object('theme') # combobox
        mobile_theme = builder.get_object('mobile_theme') # combobox
        log_level = builder.get_object('log_level')
        hostname = builder.get_object('hostname')
        port = builder.get_object('port')
        proxy = builder.get_object('proxy')
        proxy_hostname = builder.get_object('proxy_hostname')
        proxy_port = builder.get_object('proxy_port')

        self.__setup_combobox(theme)
        self.__load_themes(theme, 'theme')
        
        self.__setup_combobox(mobile_theme)
        self.__load_themes(mobile_theme, 'theme.mobile')
        
        self.__setup_combobox(log_level)
        self.__load_debug_level(log_level)
        self.__load_networking(hostname, port)
        self.__load_proxy(proxy, proxy_hostname, proxy_port)
        

        
    def save(self, builder):
        self.info('Saving configuration')
        config = self.config
        
        theme = builder.get_object('theme') # combobox
        config.put('theme', theme.get_active_text())

        mobile_theme = builder.get_object('mobile_theme') # combobox
        config.put('theme.mobile', mobile_theme.get_active_text())
        
        log_level = builder.get_object('log_level')
        config.put('log.level', log_level.get_active_text())
        
        hostname = builder.get_object('hostname')
        config.put('hostname', hostname.get_text())
        
        port = builder.get_object('port')
        config.put('port', port.get_text())
        
        proxy = builder.get_object('proxy')
        if proxy.get_active():
            is_proxy = 'True'
        else:
            is_proxy = 'False'
        config.put('proxy', is_proxy)
        
        proxy_hostname = builder.get_object('proxy_hostname')
        config.put('proxy.hostname', proxy_hostname.get_text())
        
        proxy_port = builder.get_object('proxy_port')
        config.put('proxy.port', proxy_port.get_text())

        config.save_configuration(self.config_path)

        
        
