var timers = [];

$(document).ready(function() {
	update_status();
	load_playlist();
	
	$('#play_pause').click(function() {
		$.post("rest/player", { action: "play_pause" }, function (data) {
			timers.push(setTimeout('update_status()', 100));
		});
	});
	
	$('#previous').click(function() {
		$.post("rest/player", { action: "previous" }, function (data) {
			timers.push(setTimeout('load_playlist()', 100));
			timers.push(setTimeout('update_status()', 200));
		});
	});
	
	$('#next').click(function() {
		$.post("rest/player", { action: "next" }, function (data) {
			timers.push(setTimeout('load_playlist()', 100));
			timers.push(setTimeout('update_status()', 200));
		});
	});

	$('#seek_back').click(function() {
		$.post("rest/player", { action: "seek", "time" : "-10" }, function (data) {
			timers.push(setTimeout('update_status()', 100));
		});
	});

	$('#seek_forward').click(function() {
		$.post("rest/player", { action: "seek", "time" : "10" }, function (data) {
			timers.push(setTimeout('update_status()', 100));
		});
	});
	
});


function update_status() {
	
	$.each(timers, function(index, timer) {
		clearTimeout(timer);
	});
	
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
				
				var timer_function = function () {
					actual_time++;
					
					atime = human_time(actual_time);
					str_time = atime + ' <i> of </i> ' + total_time;
					$('#time').html(str_time);
					
					if (actual_time < duration)
						timers.push(setTimeout(timer_function, 1000));
					else {
						update_status();
						timers.push(setTimeout('load_playlist()', 100));
					}
				};
				timers.push(setTimeout(timer_function, 1000));
			}
			
			countdown();
		}
		timers.push(setTimeout('update_status()', 10000));
	});
}

function load_playlist() {
	$.getJSON('rest/playlist', function(json) {
		$('#playlist').html('');
		if (json && json.entries) {
			$.each(json.entries, function(index, entry) {
				add_playlist_entry(index, entry);
			});
		}
	});
}


function add_playlist_entry(index, entry) {
	var line_id = 'track_line_' + entry.id;
	var container_id = 'track_actions_' + entry.id;
	var line = create_entry_line(line_id, container_id, entry);
	
	$('#playlist').append(line);

	// remove
	add_dequeue_action(line_id, container_id, entry);
	// rate
	// add_rate_action(line_id, container_id, entry);
}


function add_search_entry(index, entry, container) {
	var line_id = 'search_line_' + entry.id;
	var container_id = 'search_actions_' + entry.id;
	var line = create_entry_line(line_id, container_id, entry);
	
	$(container).append(line);
	
	add_enqueue_action(line_id, container_id, entry);
	// rate
	// add_rate_action(line_id, container_id, entry);
}

function create_header() {
	var line = '<div class="line">';
	line += '<span id="track_number">#</span>';
	line += '<span id="track_title">Title</span>';
	line += '<span id="track_genre">Genre</span>';
	line += '<span id="track_artist">Artist</span>';
	line += '<span id="track_album">Album</span>';
	line += '<span id="track_duration">Duration</span>';
	line += '<span id="track_actions">&nbsp;</span></span>';
	line += '</div>';
	return line;
}

function create_entry_line(line_id, container_id, entry) {
	var line = '<div id="' + line_id + '" class="line">';
	line += '<span id="track_number">' + entry.track_number + '</span>';
	line += '<span id="track_title">' + entry.title + '</span>';
	line += '<span id="track_genre">' + entry.genre + '</span>';
	line += '<span id="track_artist">' + entry.artist + '</span>';
	line += '<span id="track_album">' + entry.album + '</span>';
	line += '<span id="track_duration">' + human_time(entry.duration) + '</span>';
	line += '<span id="track_actions"><span id="' + container_id + '"></span></span>';
	line += '</div>';
	return line;
}


function add_dequeue_action(line_id, container_id, entry) {
	var action_id = container_id + '_dequeue';
	var dequeue = '<img id="' + action_id + '" class="link" src="img/remove.svg" />';
	var entry_id = entry.id;
	$('#' + container_id).append(dequeue);
	$('#' + action_id).click(function() {
		$.post("rest/player", { action: "dequeue", "entry_id" : entry_id }, function(data) {
			$('#' + line_id).fadeOut('slow');
		});
	});
}


function add_enqueue_action(line_id, container_id, entry) {
	var action_id = container_id + '_enqueue';
	var enqueue = '<img id="' + action_id + '" class="link" src="img/add.svg" />';
	var entry_id = entry.id;
	$('#' + container_id).append(enqueue);
	$('#' + action_id).click(function() {
		$.post("rest/player", { action: "enqueue", "entry_id" : entry_id }, function(data) {
			$.getJSON('rest/song/' + entry_id, function(entry) {
				// add_playlist_entry(0, entry);
				$('#' + line_id).fadeOut('slow');
			});
		});
	});
}

/*
function add_rate_action(line_id, container_id, entry) {
	var action_id = container_id + '_rate_';
	var rating;
	for(rating = 0; rating < 6; rating++) {
		var enqueue = '<img id="' + action_id + '" class="link" src="img/add.svg" />';
		var entry_id = entry.id;
		$('#' + container_id).append(enqueue);
		$('#' + action_id).click(function() {
			$.post("rest/player", { action: "enqueue", "entry_id" : entry_id }, function(data) {
				$.getJSON('rest/song/' + entry_id, function(entry) {
					add_playlist_entry(0, entry);
				});
			});
		});
	}
}
*/