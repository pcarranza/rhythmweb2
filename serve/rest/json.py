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

class JSon():
    
    name = None
    attributes = None
    
    def __init__(self):
        self.attributes = {}
        
    
    def put(self, name, value):
        self.attributes[name] = value
        
        
    def get(self, name):
        if self.attributes.has_key(name):
            return self.attributes[name]
        
        return None
    
    
    def parse(self):
        
        return_value = []
        
        attributes = self.attributes
        return_value.append(self._parse_attributes(attributes))
        
        return ''.join(return_value)
    
        
    def _parse_value(self, value):
        return_value = []
        
        if type(value) is list:
            list_value = []
            
            return_value.append('[ ')
            for v in value:
                list_value.append(self._parse_value(v))
                list_value.append(', ')
            
            if len(list_value) > 0:
                list_value = list_value[0:len(list_value)-1] # remove last element
                
            return_value.append(''.join(list_value))
            return_value.append(' ]')
            
        elif type(value) is dict:
            return_value.append(self._parse_attributes(value))
        
        elif type(value) is str:
            return_value.append("\"")
            return_value.append(self._encode_str(value))
            return_value.append("\" ")
        
        elif type(value) is bool:
            if value:
                return_value.append('true')
            else:
                return_value.append('false')
                
        elif isinstance(value, JSon):
            return_value.append(value.parse())
            
        else: # type(value) is int or type(value) is float:
            return_value.append(self._encode_str(value))
        
        return ''.join(return_value)    
    
    def _encode_str(self, value):
        value = str(value)
        value = value.replace('"', '\\"')
        return value
    
    def _parse_attributes(self, attributes):
        return_value = []
        
        return_value.append('{ ')
        
        for attr in attributes:
            return_value.append("\"")
            return_value.append(attr)
            return_value.append("\" : ")
            
            value = self.attributes[attr]
            return_value.append(self._parse_value(value))
            return_value.append(', ')
            
        if return_value[-1] == ', ':
            return_value = return_value[0:len(return_value)-1]
            
        return_value.append(' }')
            
        return ''.join(return_value)
    