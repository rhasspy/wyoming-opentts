#!/usr/bin/env sh

.venv/bin/python3 -m wyoming_opentts \
    --nanotts-bin ./local/nanotts/bin/nanotts \
    --nanotts-lang ./local/nanotts/share/pico/lang/ \
    --marytts-dir ./local/marytts/ \
    --flite-voices ./local/flite \
    --uri 'tcp://0.0.0.0:10200' "$@"
