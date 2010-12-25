var timers = [];
var library_loaded = false;


$(document).ready(function() {
	update_status();
	
	$('#play_pause').click(function() {
		$.post("rest/player", { action: "play_pause" }, function (data) {
			timers.push(setTimeout('update_status()', 200));
		});
	});
	
	$('#previous').click(function() {
		$.post("rest/player", { action: "previous" }, function (data) {
			timers.push(setTimeout('load_playlist()', 200));
			timers.push(setTimeout('update_status()', 500));
		});
	});
	
	$('#next').click(function() {
		$.post("rest/player", { action: "next" }, function (data) {
			timers.push(setTimeout('load_playlist()', 200));
			timers.push(setTimeout('update_status()', 500));
		});
	});

	$('#seek_back').click(function() {
		$.post("rest/player", { action: "seek", "time" : "-10" }, function (data) {
			timers.push(setTimeout('update_status()', 200));
		});
	});

	$('#seek_forward').click(function() {
		$.post("rest/player", { action: "seek", "time" : "10" }, function (data) {
			timers.push(setTimeout('update_status()', 200));
		});
	});
	
	$('#tab_playlist').click(function () {
		clear_tabs();
		hide_all();
		$(this).addClass('selected');
		load_playlist();
		$('#playlist').removeClass('hide');
	});
	
	$('#tab_library').click(function () {
		clear_tabs();
		hide_all();
		$(this).addClass('selected');

		if (!library_loaded) {
			load_library(0, 50);
			library_loaded = true;
		}
		
		$('#library').removeClass('hide');
	});
	
	$('#tab_search').click(function () {
		clear_tabs();
		hide_all();
		$(this).addClass('selected');
		$('#search').removeClass('hide');
	});

	$('#do_search').click(function() {
		parameters = parse_search_parameters();
		var url = 'rest/search';
		$('#search_result').html('');
		$.post(url, parameters, function(json) {
			$('#search_result').append(create_header());
			$.each(json.entries, function(index, entry) {
				add_search_entry(index, entry, 'search_result');
			});
		});
	});

	$('#search_filter').keypress(function(event) {
		  if (event.keyCode == '13') {
			  $('#do_search').click();
		  }
	});

	$('#search_filter').focus();

	
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
	});
	timers.push(setTimeout('update_status()', 10000));
}

function load_playlist() {
	$.getJSON('rest/playlist', function(json) {
		$('#playlist').html('');
		$('#playlist').append(create_header());
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

	add_rate_action(line_id, container_id, entry);
	add_dequeue_action(line_id, container_id, entry);
}


function add_search_entry(index, entry, container) {
	var line_id = container + '_line_' + entry.id;
	var container_id = line_id + '_actions';
	var line = create_entry_line(line_id, container_id, entry);
	
	$('#' + container).append(line);
	
	add_rate_action(line_id, container_id, entry);
	add_enqueue_action(line_id, container_id, entry);
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
				$('#' + line_id).fadeOut('slow');
			});
		});
	});
}


function add_rate_action(line_id, container_id, entry) {
	var entry_id = entry.id;
	var rating = entry.rating;
	var action_scheme = container_id + '_rate_';
	for(var index = 1; index < 6; index++) {
		var action_id = action_scheme + index;
		if (index > rating) {
			$('#' + container_id).append('<img id="' + action_id + '" class="link" src="img/star-grey.svg" />');
		} else {
			$('#' + container_id).append('<img id="' + action_id + '" class="link" src="img/star.svg" />');
		}
		$('#' + action_id).bind('click', { id : entry_id, rating : index, scheme : action_scheme }, set_rating);
	}
}

function set_rating(event) {
	var data = event.data;
	var action_scheme = data.scheme;
	var url = "rest/song/" + data.id;
	$.post(url, { rating : data.rating }, function(json) {
		var rating = json.rating;
		var index;
		for (index = 1; index <= 6; index++) {
			if (index <= rating) {
				$('#' + action_scheme + index).attr('src', 'img/star.svg');
			} else {
				$('#' + action_scheme + index).attr('src', 'img/star-grey.svg');
			}
		}
	});
}

function clear_tabs() {
	$('#tab_playlist').removeClass('selected');
	$('#tab_library').removeClass('selected');
	$('#tab_search').removeClass('selected');
}

function hide_all() {
	$('#playlist').addClass('hide');
	$('#library').addClass('hide');
	$('#search').addClass('hide');
}


function load_library(first, limit) {
	var url = 'rest/search/song/first/' + first + '/limit/' + limit;
	$('#library').html('');
	$.getJSON(url, function(json) {
		if (json && json.entries) {
			first = parseInt(first);
			limit = parseInt(limit);
			var count = json.entries.length;
			var prev = first - limit;
			var next = first + limit;

			if(first > 0) {
				$('#library').append('<span class="library_previous">' +
						'<img id="go_previous_top" src="img/go-previous.svg" class="link" />' + 
						'</span>');
				$('#go_previous_top').click( function() {
					load_library(prev, limit);
				});
			} else {
				$('#library').append('<span class="library_previous">' +
						'&nbsp;' +
						'</span>');
			}

			$('#library').append('<span class="library_status">showing ' + count + 
					' starting at ' + first + 
					'</span>');
			
			if (count == limit) {
				$('#library').append('<span class="library_next">' + 
						'<img id="go_next_top" src="img/go-next.svg" class="link" />' +
						'</span>');
				$('#go_next_top').click( function() {
					load_library(next, limit);
				});
			} else {
				$('#library').append('<span class="library_next">' +
						'&nbsp;' +
						'</span>');
			}

			$('#library').append(create_header());
			
			$.each(json.entries, function(index, entry) {
				add_search_entry(index, entry, 'library');
			});
			
			if(first > 0) {
				$('#library').append('<img id="go_previous" src="img/go-previous.svg" class="link">');
				$('#go_previous').click( function() {
					load_library(prev, limit);
				});
			}
			
			if (count == limit) {
				$('#library').append('<img id="go_next" src="img/go-next.svg" class="link">');
				$('#go_next').click( function() {
					load_library(next, limit);
				});
			}
		}
	});
}


function parse_search_parameters() {
	var filter = $('#search_filter').val();
	var filter_tags = /[^\[\*\s]+\:[^\]\*]+/g;
	var rating_tag = /\*{1,5}/g;
	var rating = 0;
	var filters = [];
	var clean_filter = filter;
	
	while(tag = filter_tags.exec(filter)) {
		tag = String(tag);
		tag = trim(tag);
		filters.push(tag);
		clean_filter = clean_filter.replace(tag, '');
	}

	while(rate = rating_tag.exec(filter)) {
		rate = String(rate);
		irate = rate.length;
		if (irate > rating)
			rating = irate;
		clean_filter = clean_filter.replace(rate, '');
	}
	
	while(quote = /\[\]/.exec(clean_filter)) {
		clean_filter = clean_filter.replace(quote, '');
	}
	clean_filter = trim(clean_filter);
	
	var is_type_song = /type\:song/;
	var is_type_podcast = /type\:podcast/;
	var is_type_radio = /type\:radio/;
	var is_artist = /artist:.+/;
	var is_album = /album:.+/;
	var is_title = /title:.+/;
	var is_genre = /genre:.+/;
	var is_limit = /limit:.+/;
	var is_first = /first:.+/;
	
	var query_parameters = {};
	
	if (rating > 0)
		query_parameters.rating = rating;

	if (filters.length > 0) {
		$.each(filters, function(index, value) {
			if (is_type_song.test(value)) {
				query_parameters.type = 'song';
			} else if (is_type_podcast.test(value)) {
				query_parameters.type = 'podcast';
			} else if (is_type_radio.test(value)) {
				query_parameters.type = 'iradio';
			} else if (is_artist.test(value)) {
				query_parameters.artist = value.replace(/artist:/, '');
			} else if (is_album.test(value)) {
				query_parameters.album = value.replace(/album:/, '');
			} else if (is_title.test(value)) {
				query_parameters.title = value.replace(/title:/, '');
			} else if (is_genre.test(value)) {
				query_parameters.genre = value.replace(/genre:/, '');
			} else if (is_limit.test(value)) {
				query_parameters.limit = value.replace(/.*limit:/, '');
			} else if (is_first.test(value)) {
				query_parameters.first = value.replace(/.*first:/, '');
			}
		});
		
	} 

	if (!query_parameters.hasOwnProperty('artist') && 
			!query_parameters.hasOwnProperty('album') &&
			!query_parameters.hasOwnProperty('title') &&
			!query_parameters.hasOwnProperty('genre') &&
			clean_filter)
		query_parameters.all = clean_filter;

	if (!query_parameters.type)
		query_parameters.type = 'song';

	return query_parameters;
	
}
