(function (root, factory) {
	if (typeof define === 'function' && define.amd) {
		// AMD. Register as an anonymous module.
		define(['leaflet'], factory);
	} else if (typeof modules === 'object' && module.exports) {
		// define a Common JS module that relies on 'leaflet'
		module.exports = factory(require('leaflet'));
	} else {
		// Assume Leaflet is loaded into global object L already
		factory(L);
	}
}(this, function (L) {
	'use strict';

    //https://github.com/DanielJDufour/homonyms.git
    var homonyms = {"base":["base"],"change":["change"],"close":["close","clothes"],"exit":["accent","exit"],"full":["full","pool"],"go":["go"],"in":["an","en","in","on","un"],"map":["map"],"screen":["screen"],"switch":["swetch","switch"],"out":["at","oat","oot","out","ount"],"view":["view"],"zoom":["cinnam","dom","doom","germ","jim","sum","soon","sune","superm","xoom","zimmerm","zoom","zum","zume"]};



    var commands = [];

    var re = {};
    for (let phrase in homonyms) {
        re[phrase] = "(?:" + homonyms[phrase].join("|") + ")";
    }


    re.zoom_in = new RegExp(".*" + re.zoom + " ?" + re.in + ".*", "i");
    re.zoom_out = new RegExp(".*" + re.zoom + " ?" + re.out + ".*", "i");

    re.basemap = "(?:" + re.base + "[ -]?" + re.map + ")s?";
    re.fullscreen = "(?:" + re.full + "[ -]?" + re.screen + ")";

    re.go_full_screen = new RegExp(".*" + "(?:" + re.go + "|" + re.view + ")" + " ?" + re.fullscreen + ".*", "i");
    re.exit_fullscreen = new RegExp(".*" + "(?:" + re.exit + ")" + " ?" + re.fullscreen + ".*", "i");
    re.switch_basemap = new RegExp(".*" + "(?:" + re.switch + "|" + re.change + ")" + " ?" + re.basemap + ".*", "i");


    L.Voice = {


        addTo: function(map) {
            this.maps.push(map);
        },

        commands: {
            zoom_in: {
                pattern: re.zoom_in,
                action: function() {
                    L.Voice.maps.forEach(function(map) {
                        map.zoomIn();
                    });
                }
            },
            zoom_out: {
                pattern: re.zoom_out,
                action: function() {
                    L.Voice.maps.forEach(function(map) {
                        map.zoomOut();
                    });
                }
            },
            exit_fullscreen: {
                pattern: re.exit_fullscreen,
                action: function() {
                    var map = L.Voice.maps[0];
                    if (map.isFullscreen && map.isFullscreen()) {
                        map.toggleFullscreen();
                    }
                }
            },
            switch_basemap: {
                pattern: re.switch_basemap,
                action: function() {
                    console.log("switching basemap");
                }
            }
        },

        debug: true,

        initialize: function() {
            var Voice = this;

            this.recognition = new (window.SpeechRecognition||window.webkitSpeechRecognition||window.mozSpeechRecognition||window.msSpeechRecognition)();
            this.recognition.continuous = true;
            this.recognition.lang = 'en-US';
            this.recognition.interimResults = true;
            this.recognition.maxAlternatives = 5;

            this.recognition.onerror = function(event) {
                console.log("errored", event);
                Voice.restart();
            };

            this.recognition.onend = function(event) {
                console.log("errored", event);
                Voice.restart();
            };

            this.recognition.onresult = function(event) {
                var speechRecognitionResultList = event.results;
                var transcript = speechRecognitionResultList[speechRecognitionResultList.length - 1][0].transcript;
                console.log("captured", transcript);
                var commands = Voice.commands;
                for (var key in commands) {
                    if (commands.hasOwnProperty(key)) {
                        var value = commands[key];
                        if (transcript.match(value.pattern)) {
                            value.action();
                            Voice.stop();
                            Voice.restart();
                            return;
                        }
                    }
                }
            };
        },

        maps: [],

        patterns: {
            close: close
        },

        restart: function(event) {
           if (this.debug) console.log("restarting L.Voice");
           var Voice = this;
           if (Voice._status != "restarting") {
               var current_time = new Date().getTime();
               setTimeout(function() {
                   Voice.start();
                   Voice._status = "running";
               }, 1000);
               Voice._status = "restarting";
           }
        },

        _status: "stopped",

        start: function() {
            this.recognition.start();
            $(".leaflet-control-voice-commands a").css("color", "red");
        },

        stop: function() {
            this.recognition.stop();
            $(".leaflet-control-voice-commands a").css("color", "black");
        }
    };

    L.Voice.initialize();


    L.Control.Voice = L.Control.extend({
        options: {
            position: 'topleft',
            title: {
                'false': 'Enable Voice Commands',
                'true': 'Disable Voice Commands'
            }
        },

        onAdd: function (map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-voice-commands');

            this.link = L.DomUtil.create('a', 'fa fa-microphone fa-2 leaflet-bar-part', container);
            this.link.style.fontSize = "14pt";
            this.link.href = '#';

            this._map = map;
            L.Voice.addTo(map);
            //this._map.on('listening-for-voice-commands', this._toggleTitle, this);
            //this._toggleTitle();

            L.DomEvent.on(this.link, 'click', this._click, this);

            return container;
        },

        _click: function (e) {
            L.DomEvent.stopPropagation(e);
            L.DomEvent.preventDefault(e);
            var _status = L.Voice._status;
            if (_status === "running") {            
                L.Voice.stop();
            } else if (_status === "restarting") {
                L.Voice.stop();
            } else if (_status === "stopped") {
                L.Voice.start();
            }
        },

        _toggleTitle: function() {
            this.link.title = this.options.title[this._map.isFullscreen()];
        }
    });

    L.Map.mergeOptions({
        voiceControl: false
    });

    L.Map.addInitHook(function () {
        if (this.options.voiceControl) {
            this.voiceControl = new L.Control.Voice(this.options.voiceControl);
            this.addControl(this.voiceControl);
        }
    });

    L.control.voice = function (options) {
        return new L.Control.Voice(options);
    };

    return L;
}));
