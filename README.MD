# DI.FM Web UI / API for Chromecast Devices 
A little flask app that interacts with di.fm and your chromecasts. It provides a trivial API for playing channels, changing volume and stopping music.
It also has a simple web interface to control everything. 

It now also includes difmiftt.py which is an API designed for IFTT integration. By creating a new applet,
you can use Google Assistant as the trigger, and a POST request as the action (WebHook).

i.e. POST {"key":"akeyinsecrets.py","channel":"lounge"} /api/play

Must have a premium DI.FM account to get the API key (the key at the end of direct URLs in the PLS files)

MIT license