var timer;

$(document).ready(function() {
	update_status();
	
	$('#play_pause').click(function() {
		$.post("rest/player", { action: "play_pause" }, function (data) {
			setTimeout('update_status()', 500);
		});
	});
	
	$('#previous').click(function() {
		$.post("rest/player", { action: "previous" }, function (data) {
			setTimeout('update_status()', 500);
		});
	});
	
	$('#next').click(function() {
		$.post("rest/player", { action: "next" }, function (data) {
			setTimeout('update_status()', 500);
		});
	});

	$('#seek_back').click(function() {
		$.post("rest/player", { action: "seek", "time" : "-10" }, function (data) {
			setTimeout('update_status()', 500);
		});
	});

	$('#seek_forward').click(function() {
		$.post("rest/player", { action: "seek", "time" : "10" }, function (data) {
			setTimeout('update_status()', 500);
		});
	});
	
});


function update_status() {
	if (timer !== undefined) {
		clearTimeout(timer);
	}

	$.getJSON('rest/status', function(json) {
		if (json && json.playing) {
			$('#play').hide();
			$('#pause').show();
		} else {
			$('#play').show();
			$('#pause').hide();
		}

		if (json && json.playing) {
			
			var artist = '';
			var album = '';
			var title = '';
			var time = 0;
			var total_time = 0;
			
			if (json && json.playing_entry) {
				entry = json.playing_entry;
				if (entry.title) {
					title = entry.title;
				}
				if (entry.artist) {
					artist = 'by <i>' + entry.artist + '</i>';
				}
				if (entry.album) {
					album = 'from <i>' + entry.album + '</i>';
				}
			}

			$('#artist').html(artist);
			$('#album').html(album);
			$('#title').html(title);

			var countdown = function() {
				
				var duration = entry.duration;
				var total_time = human_time(duration)
				var actual_time = json.playing_time;
				var time_check = 0;
				
				var timer_function = function () {
					if (time_check > 30) {
						update_status();
					}
					
					time_check++;
					actual_time++;
					
					atime = human_time(actual_time);
					str_time = atime + ' <i> of </i> ' + total_time;
					$('#time').html(str_time);
					
					if (actual_time < duration)
						timer = setTimeout(timer_function, 1000);
					else
						update_status();
				};
				timer = setTimeout(timer_function, 1000);
			}
			
			countdown();
		}
	});
}



