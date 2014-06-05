#!/bin/bash

host=$1
port=${2:-"7000"}

if [ -z $host ]; then
    echo "Must provide a host to connect to"
    exit 1
fi

echo "Using host $host and port $port"

cat <<EOF
Test 1

curl -g http://$host:$port/rest/status

Should Return:
{
   "muted" : false,
   "volume" : 0.5,
   "playing_order" : "shuffle",
   "playing" : false
}

EOF

echo "------------------------------------------"

cat <<EOF
Test 2

curl -g http://$host:$port/rest/status

Returns:
{
   "muted" : false,
   "volume" : 0.5,
   "playing_order" :  "shuffle",
   "playing_entry" :  {
      "album" :  "Blood Sugar Sex Magik", 
      ...
   },
   "playing_time" : 76,  "playing" : true
}

EOF

echo "------------------------------------------"

cat <<EOF
Test 3 - Get a song

curl -g http://$host:$port/rest/song/6526

Gets a song

EOF

echo "------------------------------------------"

cat <<EOF
Test 4 - Get the queue

curl -g http://$host:$port/rest/queue

Returns:
{
   "entries" :  [ ... ]
}

EOF

echo "------------------------------------------"

cat <<EOF
Test 5 - Get playlists

curl -g http://$host:$port/rest/playlists

Returns:
{
   "playlists" :  [ {
      "is_playing" : false,
      "is_group" : false,
      "id" : 0,
      "visibility" : true,
      "name" :  "Añadidos recientemente"
   },  ...  ]  
}

EOF

echo "------------------------------------------"

cat <<EOF
Test 6 - Get one playlist

curl -g http://$host:$port/rest/playlists/0

Returns:
{
   "is_playing" : false,
   "is_group" : false,
   "id" : 0,
   "visibility" : true,
   "name" : "Añadidos recientemente",
   "entries" : [ ... ] }
}

EOF

echo "------------------------------------------"

cat <<EOF
Test 7 - Enqueue a playlist

curl -d action=enqueue -d playlist=1 http://$host:$port/rest/playlists

Returns:
{ "count" : 10, "result" : "OK" }

EOF

echo "------------------------------------------"

cat <<EOF
Test 8 - Start or stop playing

curl -d action=play_pause http://$host:$port/rest/player

EOF

cat <<EOF
Test 9 - Forward time 10 seconds

curl -d action=seek -d time=10 http://$host:$port/rest/player

EOF

echo "------------------------------------------"

cat <<EOF
Test 10 - Query first 10 songs

curl -g http://$host:$port/rest/search/song/limit/10

Returns:
{  "entries" :  [ ... ] }

curl -d type=song -d limit=10 http://$host:$port/rest/search

Returns:
{  "entries" :  [ ... ] }

EOF

echo "------------------------------------------"

cat <<EOF
Test 11 - Query library

curl -g http://$host:$port/rest/library/artists

Returns:
{ 
   "biggest_artist" : { "name" : "The Roots" , "value" : 218 }, 
   "artists" : [ ... ]
}

EOF

echo "------------------------------------------"

cat <<EOF
Test 12 - Query for one artist

curl -g http://$host:$port/rest/library/artists/The+Roots

Returns:
{ "entries" : [ ... ], "artists" : "The Roots" }

EOF

echo "------------------------------------------"

cat <<EOF
Test 12 - Rate a song

curl -d rating=1 http://$host:$port/rest/song/2

EOF
