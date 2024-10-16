# Wyoming openTTS

[Wyoming protocol](https://github.com/rhasspy/wyoming) some of the text-to-speech systems from [openTTS](https://github.com/synesthesiam/opentts):

* [nanoTTS](https://github.com/gmn/nanotts)
    * English (2), German (1), French (1), Italian (1), Spanish (1)
* [MaryTTS](http://mary.dfki.de)
    * English (7), German (3), French (4), Italian (1), Russian (1), Swedish (1), Telugu (1), Turkish (1)
    * Includes [embedded MaryTTS](https://github.com/synesthesiam/marytts-txt2wav)
    * **NOTE:** May require too much RAM for the Raspberry Pi Zero and Zero 2
* [flite](http://www.festvox.org/flite)
    * English (19), Hindi (1), Bengali (1), Gujarati (3), Kannada (1), Marathi (2), Punjabi (1), Tamil (1), Telugu (3)
* [Festival](http://www.cstr.ed.ac.uk/projects/festival/)
    * English (9), Spanish (1), Catalan (1), Czech (4), Russian (1), Finnish (2), Marathi (1), Telugu (1), Hindi (1), Italian (2), Arabic (2)
    * Spanish/Catalan/Finnish use [ISO-8859-15 encoding](https://en.wikipedia.org/wiki/ISO/IEC_8859-15)
    * Czech uses [ISO-8859-2 encoding](https://en.wikipedia.org/wiki/ISO/IEC_8859-2)
    * Russian is [transliterated](https://pypi.org/project/transliterate/) from Cyrillic to Latin script automatically
* [eSpeak](http://espeak.sourceforge.net)
    * Supports huge number of languages/locales, but sounds robotic


## Home Assistant Add-on

[![Show add-on](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=47701997_opentts&repository_url=https%3A%2F%2Fgithub.com%2Frhasspy%2Fhassio-addons)

[Source](https://github.com/rhasspy/hassio-addons/tree/master/opentts)

## Docker Image

``` sh
docker run -it -p 10400:10400 rhasspy/wyoming-opentts
```

[Source](https://github.com/rhasspy/wyoming-addons/tree/master/opentts)

## Manual Installation

See the `Dockerfile` for installation details (Debian). Voice resources are available [here](https://github.com/synesthesiam/opentts/releases/download/v2.1/). nanoTTS is available for multiple CPU architectures [here](https://github.com/synesthesiam/opentts).
