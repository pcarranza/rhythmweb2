/*
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
*/

function human_time(seconds) {
	if (seconds < 60)
		return '' + seconds;

	minutes = seconds / 60;
	minutes = Math.floor(minutes);

	secs = seconds % 60;
	secs = '0' + secs
	secs = secs.slice(secs.length - 2);
	return minutes + ':' + secs;
}

function trim(myString) {
	return myString.replace(/^\s+/g, '').replace(/\s+$/g, '');
}

function dumpObject(obj) {
	return dumpObjectIndented(obj, "  ");
}

function dumpObjectIndented(obj, indent) {
	var result = "";
	if (indent == null)
		indent = "";

	for (var property in obj) {
		var value = obj[property];
		if (typeof value == 'string')
			value = "'" + value + "'";
		else if (typeof value == 'object') {
			if (value instanceof Array) {
				// Just let JS convert the Array to a string!
				value = "[ " + value + " ]";
			} else {
				var od = DumpObjectIndented(value, indent + "  ");
				value = "\n" + indent + "{\n" + od + "\n" + indent + "}";
			}
		}
		result += indent + "'" + property + "' : " + value + ",\n";
	}
	return result.replace(/,\n$/, "");
}
