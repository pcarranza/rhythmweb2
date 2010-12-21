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
