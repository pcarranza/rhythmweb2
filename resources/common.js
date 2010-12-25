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
	return myString.replace(/^\s+/g,'').replace(/\s+$/g,'');
}

function dumpObject(obj) {
	return dumpObjectIndented(obj, "   ");
}

function dumpObjectIndented(obj, indent)
{
  var result = "";
  if (indent == null) indent = "";

  for (var property in obj)
  {
    var value = obj[property];
    if (typeof value == 'string')
      value = "'" + value + "'";
    else if (typeof value == 'object')
    {
      if (value instanceof Array)
      {
        // Just let JS convert the Array to a string!
        value = "[ " + value + " ]";
      }
      else
      {
        // Recursive dump
        // (replace "  " by "\t" or something else if you prefer)
        var od = DumpObjectIndented(value, indent + "  ");
        // If you like { on the same line as the key
        //value = "{\n" + od + "\n" + indent + "}";
        // If you prefer { and } to be aligned
        value = "\n" + indent + "{\n" + od + "\n" + indent + "}";
      }
    }
    result += indent + "'" + property + "' : " + value + ",\n";
  }
  return result.replace(/,\n$/, "");
}