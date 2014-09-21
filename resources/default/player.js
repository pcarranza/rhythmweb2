var timers = [];
var clear_status = null;
var volume = null;
var muted = null;

$(document).ready(function() {
	update_status();
	clear_info();
	
	$('#play_pause').click(function() {
		$.post("rest/player", { action: "play_pause" }, function (data) {
			timers.push(setTimeout('update_status()', 200));
			info('<i>play/pause</i>');
		});
	});
	
	$('#previous').click(function() {
		$.post("rest/player", { action: "previous" }, function (data) {
			timers.push(setTimeout('load_queue()', 200));
			timers.push(setTimeout('update_status()', 500));
			info('<i>previous...</i>');
		});
	});
	
	$('#next').click(function() {
		$.post("rest/player", { action: "next" }, function (data) {
			timers.push(setTimeout('load_queue()', 200));
			timers.push(setTimeout('update_status()', 500));
			info('<i>next...</i>');
		});
	});
	
	
	$('#seek_back').click(function() {
		$.post("rest/player", { action: "seek", "time" : "-10" }, function (data) {
			timers.push(setTimeout('update_status()', 200));
			info('<i>back 10 seconds</i>');
		});
	});

	$('#seek_forward').click(function() {
		$.post("rest/player", { action: "seek", "time" : "10" }, function (data) {
			timers.push(setTimeout('update_status()', 200));
			info('<i>ahead 10 seconds</i>');
		});
	});
	
	
	$('#tab_queue').click(function () {
		clear_tabs();
		hide_all();
		$(this).addClass('selected');
		load_queue();
		$('#queue').removeClass('hide');
	});
	
	
	$('#tab_tags').click(function () {
		clear_tabs();
		hide_all();
		$(this).addClass('selected');

		load_tag_cloud();
		
		$('#tags').removeClass('hide');
	});
	
	$('#tab_sources').click(function() {
		clear_tabs();
		hide_all()
		$(this).addClass('selected');
		
		load_sources();
		
		$('#sources').removeClass('hide');
	});

	
	$('#tab_search').click(function () {
		clear_tabs();
		hide_all();
		$(this).addClass('selected');
		$('#search').removeClass('hide');
	});
	

	$('#do_search').click(function() {
		parameters = parse_search_parameters();
		do_search(parameters);
	});
	
	
	$('#search_filter').keypress(function(event) {
		  if (event.keyCode == '13') {
			  $('#do_search').click();
		  }
	});
	
	$('#vol_down').click(function() {
		set_volume(-0.1);
	});
	
	$('#vol_up').click(function() {
		set_volume(0.1);
	});
	
	$('#vol_status').click(function() {
		toggle_mute();
	});

	$('#search_filter').focus();
});


function toggle_mute() {
	if (muted) {
		info('Unmuting...')
	} else {
		info('Muting...')
	}
	
	$.post("rest/player", { action: "mute" }, function(data) {
		update_status();
	});
}


function set_volume(step) {
	var new_volume;
	
	if (!volume)
		new_volume = 0;
	else
		new_volume = volume;
	
	new_volume += step;
	
	if (new_volume < 0)
		new_volume = 0;
	else if (new_volume > 1)
		new_volume = 1;
	
	new_volume = Math.round(new_volume*100)/100;
	
	$.post("rest/player", { action: "set_volume", "volume" : new_volume }, function(data) {
		info('Volume ' + (new_volume * 100) + '%');
		update_status();
	});
}


function do_search(parameters) {
	info('<i>searching...</i>');
	var url = 'rest/search';
	$('#search_result').html('');
	$('#search_result').append(search_parameters_to_html(parameters));
	$('#search_result').append('<img id="img_searching" src="img/loading.gif" width="16" height="16" alt="Searching..." title="Searching..." />');
	$.post(url, parameters, function(json) {
		$('#img_searching').hide();
		$('#search_parameters').append(
				'<span class="cell">' +
				'<span class="prop">count</span>:' + 
				'<span class="val">' + json.entries.length + '</span>' + 
				'</span>');
		$('#search_result').append(create_header('search_header_actions'));
		$('#search_header_actions').append(create_add_all('search_add_all'))
		var ids = '';
		$.each(json.entries, function(index, entry) {
			add_search_entry(index, entry, 'search_result', true);
			ids += entry.id + ',';
		});
		if (ids.length > 0)
			ids = ids.slice(0, ids.length - 1);
		$('#search_add_all').click(function() {
			$.post("rest/player", { action: "enqueue", "entry_id" : ids }, function(data) {
				var numbers = /\d+/g; 
				while(id = numbers.exec(ids)) {
					$('#search_result_line_' + id).fadeOut('fast');
				}
				info('<i>search result added to queue</i>');
			});
		}); 
	});
}


function create_add_all(id) {
	return '<img id="' + id + '" src="img/apply.png" width="24" height="24" class="link" alt="Add All" title="Add all to queue"/>'
}


function create_remove_all(id) {
	return '<img id="' + id + '" src="img/clear.png" width="24" height="24" class="link" alt="Clear queue" title="Remove all from queue"/>'
}

function create_shuffle_queue(id) {
	return '<img id="' + id + '" src="img/shuffle.png" width="24" height="24" class="link" alt="Shuffle queue" title="Shuffle playing queue"/>'
}


function search_parameters_to_html(parameters) {
	var component = '<div id="search_parameters" class="line"><span class="searchfor">Searching for: </span>';
	for(var property in parameters) {
		var value = parameters[property];
		component += '<span class="cell">' +
					'<span class="prop">' + property + '</span>:' + 
					'<span class="val">' + value + '</span>' + 
					'</span>';
	}
	component += '</div>';
	return component;
}


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
		
		
		if (json && json.volume) {
			volume = json.volume;
			volume = Math.round(volume*100)/100;
		} else {
			volume = 0;
		}

		if (json && json.muted) {
			muted = true;
			$('#vol_status').attr('title', 'Muted')
			$('#vol_status').attr('src', 'img/volume-muted.png');
		} else {
			muted = false;
			$('#vol_status').attr('title', 'Volume: ' + (volume * 100) + '%')
			if (volume > 0.79) {
				// high
				$('#vol_status').attr('src', 'img/volume-high.png');
			} else if (volume > 0.49) {
				// medium
				$('#vol_status').attr('src', 'img/volume-medium.png');
			} else if (volume > 0.19) {
				// low
				$('#vol_status').attr('src', 'img/volume-low.png');
			} else {
				// muted
				$('#vol_status').attr('src', 'img/volume-muted.png');
			}
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
					
					if (duration == 0 || actual_time < duration)
						timers.push(setTimeout(timer_function, 1000));
					else {
						update_status();
						timers.push(setTimeout('load_queue()', 100));
					}
				};
				timers.push(setTimeout(timer_function, 1000));
			}
			
			countdown();
		}
	}).fail(handle_jquery_failure);
	timers.push(setTimeout('update_status()', 10000));
}


function info(message) {
	if (clear_status) {
		clearTimeout(clear_status);
		clear_info('fast', message);
		clear_status = null;
	} else {
		$('#status_feedback').html(message);
		$('#status_feedback').fadeIn('slow');
	}
	clear_status = setTimeout('clear_info("slow")', 2000);
}


function clear_info(speed, message) {
	$('#status_feedback').fadeOut(speed, function() {
		if (message) {
			$('#status_feedback').html(message);
			$('#status_feedback').fadeIn('slow');
		}
	});
}


function load_queue() {
	$.getJSON('rest/queue', function(json) {
		$('#queue').html('');
		$('#queue').append(create_header('queue_header_actions'));
		$('#queue_header_actions').append(create_remove_all('clear_queue'));
		$('#queue_header_actions').append(create_shuffle_queue('shuffle_queue'));
		if (json && json.entries) {
			$.each(json.entries, function(index, entry) {
				add_queue_entry(index, entry);
			});
		}
		
		$('#clear_queue').click(function() {
			$.post("rest/player", {action : "clear_queue"}, function(data) {
				info('<i>play queue cleared</i>');
				$('#queue').html('');
			});
		});
		
		$('#shuffle_queue').click(function() {
			$.post("rest/player", { action: "shuffle_queue" }, function (data) {
				timers.push(setTimeout('load_queue()', 500));
				timers.push(setTimeout('update_status()', 500));
				info('<i>playing queue shuffled</i>');
			});
		});

	}).fail(handle_jquery_failure);
}


function add_queue_entry(index, entry) {
	var line_id = 'track_line_' + entry.id;
	var container_id = 'track_actions_' + entry.id;
	var rating_id = 'track_rating_' + entry.id;
	
	create_entry_line('queue', line_id, container_id, rating_id, entry);

	add_dequeue_action(line_id, container_id, entry);
	add_play_entry_action(line_id, container_id, entry);
	
	add_rate_action(line_id, rating_id, entry);
}


function add_search_entry(index, entry, container, fadeout) {
	var line_id = container + '_line_' + entry.id;
	var container_id = line_id + '_actions';
	var rating_id = line_id + '_rating';
	create_entry_line(container, line_id, container_id, rating_id, entry);
	
	add_enqueue_action(line_id, container_id, entry, fadeout);
	add_play_entry_action(line_id, container_id, entry);
	
	add_rate_action(line_id, rating_id, entry);
}


function create_header(actions_id) {
	var line = '<div class="line">';
	line += '<span class="track_actions" id="' + actions_id + '"></span>';
	line += '<span class="track_number">#</span>';
	line += '<span class="track_title">Title</span>';
	line += '<span class="track_genre">Genre</span>';
	line += '<span class="track_artist">Artist</span>';
	line += '<span class="track_album">Album</span>';
	line += '<span class="track_duration">Duration</span>';
	line += '<span class="track_rating">&nbsp;</span>';
	line += '</div>';
	return line;
}


function create_entry_line(append_to, line_id, container_id, rating_id, entry) {
	var line = '<div id="' + line_id + '" class="line">';
	line += '<span class="track_actions"><span id="' + container_id + '"></span></span>';
	line += '<span class="track_number">' + entry.track_number + '</span>';
	line += '<span class="track_title">' + entry.title + '</span>';
	line += '<span class="track_genre link" id="' + line_id +'_genre" title="browse genre">' + 
			entry.genre + '</span>';
	line += '<span class="track_artist link" id="' + line_id +'_artist"  title="browse artist">' + 
			entry.artist + '</span>';
	line += '<span class="track_album link" id="' + line_id +'_album"  title="browse album">' + 
			entry.album + '</span>';
	line += '<span class="track_duration">' + human_time(entry.duration) + '</span>';
	line += '<span class="track_rating"><span id="' + rating_id + '"></span></span>';
	line += '</div>';
	
	$('#' + append_to).append(line);
	
	$('#' + line_id + '_genre').bind('click', { type : 'genre', 'name' : entry.genre }, cloud_search);
	$('#' + line_id + '_artist').bind('click', { type : 'artist', 'name' : entry.artist }, cloud_search);
	$('#' + line_id + '_album').bind('click', { type : 'album', 'name' : entry.album }, cloud_search);
	
	return line;
}


function add_dequeue_action(line_id, container_id, entry) {
	var action_id = container_id + '_dequeue';
	var dequeue = '<img id="' + action_id + '" class="link dequeue" src="img/remove.png" ' + 
			'width="24" height="24" alt="Remove" title="Remove from queue" />';
	var entry_id = entry.id;
	$('#' + container_id).append(dequeue);
	$('#' + action_id).click(function() {
		$.post("rest/player", { action: "dequeue", "entry_id" : entry_id }, function(data) {
			$('#' + line_id).fadeOut('fast');
			info('\"' + entry.title + '\" <i>removed from queue</i>');
		});
	});
}


function add_enqueue_action(line_id, container_id, entry, fadeout) {
	var action_id = container_id + '_enqueue';
	var enqueue = '<img id="' + action_id + '" class="link enqueue" src="img/add.png" ' + 
			'width="24" height="24" alt="Add" title="Add to queue"/>';
	var entry_id = entry.id;
	$('#' + container_id).append(enqueue);
	$('#' + action_id).click(function() {
		$.post("rest/player", { action: "enqueue", "entry_id" : entry_id }, function(data) {
			info('\"' + entry.title + '\" <i>added to queue</i>');
			if (fadeout)
				$('#' + line_id).fadeOut('fast');
		});
	});
}

function add_play_entry_action(line_id, container_id, entry) {
	var action_id = container_id + '_play';
	var play_entry = '<div id="' + action_id + '" class="link play" alt="Play entry" ' + 
			'title="Play directly">&nbsp;</div>';
	var entry_id = entry.id;
	$('#' + container_id).append(play_entry);
	$('#' + action_id).click(function() {
		$.post("rest/player", { action: "play_entry", "entry_id" : entry_id }, function(data) {
			info('\"' + entry.title + '\" <i>started playing</i>');
			timers.push(setTimeout('update_status()', 500));
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
			$('#' + container_id).append(
				'<img id="' + action_id + '" class="link" src="img/star-grey.png" ' + 
				'width="24" height="24" alt="Rate" title="Rate" />');
		} else {
			$('#' + container_id).append(
				'<img id="' + action_id + '" class="link" src="img/star.png" ' + 
				'width="24" height="24" alt="Rate" title="Rate" />');
		}
		$('#' + action_id).bind(
			'click', 
			{ id : entry_id, rating : index, scheme : action_scheme }, 
			set_rating);
	}
}


function set_rating(event) {
	var data = event.data;
	var action_scheme = data.scheme;
	var url = "rest/song/" + data.id;
	$.post(url, { rating : data.rating }, function(json) {
		var rating = json.rating;
		info('<i>setting rating to ' + rating + '</i>')
		var index;
		for (index = 1; index <= 6; index++) {
			if (index <= rating) {
				$('#' + action_scheme + index).attr('src', 'img/star.png');
			} else {
				$('#' + action_scheme + index).attr('src', 'img/star-grey.png');
			}
		}
	});
}


function clear_tabs() {
	$('#tab_queue').removeClass('selected');
	$('#tab_search').removeClass('selected');
	$('#tab_tags').removeClass('selected');
	$('#tab_sources').removeClass('selected');
}


function hide_all() {
	$('#queue').addClass('hide');
	$('#search').addClass('hide');
	$('#tags').addClass('hide');
	$('#sources').addClass('hide');
}


function load_tag_cloud() {
	$('#artists_cloud').html('');
	$('#albums_cloud').html('');
	$('#genres_cloud').html('');
	
    var index = 0;
	$.getJSON('rest/library/artists', function(json) {
		biggest_value = json.max;
        $.each(json.values, function(name, value) {
            clazz = get_tag_cloud_class(value, biggest_value);
            id = 'ar_' + index; index++;
            $('#artists_cloud').append('<div id="' + 
                    id + '" class="tag_ar ' + 
                    clazz + '" title="artist: ' + name + ' [' + value + ']">' + 
                    name + '</div>');
            $('#' + id).bind('click', { type : 'artist', 'name' : name }, cloud_search);
        });
		
	}).fail(handle_jquery_failure);
	
    index = 0;
	$.getJSON('rest/library/albums', function(json) {
		biggest_value = json.max;
		
        $.each(json.values, function(name, value) {
            clazz = get_tag_cloud_class(value, biggest_value);
			id = 'al_' + index; index++;
			$('#albums_cloud').append('<div id="' + id + 
					'" class="tag_al ' + clazz + 
					'" title="album: ' + name + ' [' + value + ']">' + name + 
					'</div>');
			$('#' + id).bind('click', { type : 'album', 'name' : name }, cloud_search);			
		});
		
	}).fail(handle_jquery_failure);

    index = 0;
	$.getJSON('rest/library/genres', function(json) {
		biggest_value = json.max;
		
        $.each(json.values, function(name, value) {
            clazz = get_tag_cloud_class(value, biggest_value);
			id = 'gr_' + name; index++;
			$('#genres_cloud').append('<div id="' + id + 
					'" class="tag_gr ' + clazz + 
					'" title="genre: ' + name + ' [' + value + ']">' + name + 
					'</div>');
			$('#' + id).bind('click', { type : 'genre', 'name' : name }, cloud_search);			
		});
		
	}).fail(handle_jquery_failure);

}


function load_sources() {
	$('#sources').html('')
	$.getJSON('rest/playlists', function(json) {
		$.each(json.playlists, function(index, source) {
			add_source('sources', source);
		});
	}).fail(handle_jquery_failure);
}



function add_play_entry_action(line_id, container_id, entry) {
	var action_id = container_id + '_play';
	var play_entry = '<div id="' + action_id + 
			'" class="link play" alt="Play entry" ' + 
			'title="Play directly">&nbsp;</div>';
	var entry_id = entry.id;
	$('#' + container_id).append(play_entry);
	$('#' + action_id).click(function() {
		$.post("rest/player", 
				{ action: "play_entry", "entry_id" : entry_id }, 
				function(data) {
			info('\"' + entry.title + '\" <i>started playing</i>');
			timers.push(setTimeout('update_status()', 500));
		});
	});
}


function add_source(container, source) {
	var play_source_action = 'play_source_' + source.id;
	var play_source = '<div id="' + play_source_action + 
			'" class="link play" alt="Play source" ' + 
			'title="Play source">&nbsp;</div>';
	
	var pl_entries_id = 'pl_entries_' + source.id;
	var pl_load_source_id = 'pl_load_' + source.id;
	var pl_entries = '<div id="' + pl_entries_id + '" class="pl_entries">' + 
			'<img id="' + pl_load_source_id + '" src="img/add.png" ' + 
					'class="link pl_load" width="24" height="24" ' + 
					'alt="Show" title="Show entries" />' + 
		'</div>';

	row = '<div class="pl_row">' +
			'<div id="playlist_' + source.id + 
						'" class="pl_name" title="Enqueue source">' + 
				'<img id="do_source_' + source.id + 
						'" src="img/apply.png" width="24" height="24" ' + 
						'alt="Enqueue source" title="Enqueue source" class="enqueue"/>' +
				play_source + 
			'</div>' +
			'<div id="pl_source_name_' + source.id + 
						'" class="link pl_name" ' + 
						'title="Show entries">' + 
						(source.is_playing ? '<i>[' + source.name + ']</i>' : source.name ) + '</div>' +
				pl_entries +
			'</div>';
	$('#' + container).append(row);
	$('#do_source_' + source.id).click(function () {
		$.post("rest/playlists", 
				{ action: "enqueue", "source" : source.id }, 
				function (data) {
			info('<i>Source <b>' + source.name + '</b> added to play queue</i>');
			$('#' + pl_entries_id).fadeOut('fast');
			$('#' + pl_entries_id).html(pl_entries);
			$('#' + pl_entries_id).fadeIn('fast');
			$('#' + pl_load_source_id).bind(
					'click', 
					{ id : source.id  }, 
					load_source);
		});
	});
	$('#' + pl_load_source_id).bind(
			'click', 
			{ id : source.id  }, 
			load_source);

	$('#pl_source_name_' + source.id).bind(
			'click', 
			{ id : source.id  }, 
			load_source);
	
	$('#' + play_source_action).click(function() {
		$.post("rest/playlists", 
				{ action: "play_source", "source" : source.id }, 
				function(data) {
			info('Source <b>' + source.name + '</b> <i>started playing</i>');
			timers.push(setTimeout('update_status()', 500));
		});
	});
}


function load_source(event) {
	var source = event.data;
	var url = 'rest/playlists/' + source.id;
	var entries_id = 'pl_entries_' + source.id;
	$('#' + entries_id).html(
			'<img id="img_searching" src="img/loading.gif" width="16" height="16" ' + 
					'alt="Fetching source..." title="Fetching source..." />');
	$.getJSON(url, function(json) {
		var header_actions = 'source_' + source.id + '_header_actions';
		$('#' + entries_id).html('');
		$('#' + entries_id).append(create_header(header_actions));
		$.each(json.entries, function(index, entry) {
			add_search_entry(index, entry, entries_id, true);
		});
		
	}).fail(handle_jquery_failure);
	
}


function cloud_search(event) {
	data = event.data;
	var filter;
	if (data.type == 'artist') {
		filter = '[artist:' + data.name + ']';
	} else if (data.type == 'album') {
		filter = '[album:' + data.name + ']';
	} else {
		filter = '[genre:' + data.name + ']';
	}
	filter += ' [limit:100] [type:song]';
	
	clear_tabs();
	hide_all();
	$('#tab_search').addClass('selected');
	$('#search_filter').val(filter);
	$('#search').removeClass('hide');
	$('#do_search').click();
}


function get_tag_cloud_class(value, max_value) {
	percent = value / max_value;
	if (percent > 0.9) {
		return 'xxx_large';
	} else if (percent > 0.7) {
		return 'xx_large';
	} else if (percent > 0.5) {
		return 'x_large';
	} else if (percent > 0.4) {
		return 'large';
	} else if (percent > 0.3) {
		return 'medium';
	} else if (percent > 0.2) {
		return 'small';
	} else if (percent > 0.1) {
		return 'x_small';
	} else {
		return 'xx_small';
	}

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
				query_parameters.type = 'radio';
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
			clean_filter) {
		
		query_parameters.all = clean_filter;
		
	} else if (clean_filter) {
		
		if (!query_parameters.hasOwnProperty('artist'))
			query_parameters.artist = clean_filter;
		
		else if (!query_parameters.hasOwnProperty('album'))
			query_parameters.album = clean_filter;
		
		else if (!query_parameters.hasOwnProperty('title'))
			query_parameters.title = clean_filter;
		
	}

	if (!query_parameters.type)
		query_parameters.type = 'song';

	return query_parameters;
	
}

function handle_jquery_failure(jqxhr, textStatus, error) {
    console.log('Error');
    console.log(jqxhr);
    console.log(textStatus);
    console.log(error);
}
