#!/usr/bin/env python3
import argparse
import asyncio
import io
import logging
import shutil
import time
import wave
from functools import partial
from pathlib import Path
from typing import Dict, Optional

from wyoming.audio import wav_to_chunks
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.tts import Synthesize

from .tts import EspeakTTS, FestivalTTS, FliteTTS, MaryTTS, NanoTTS, TTSBase

_LOGGER = logging.getLogger()
_DIR = Path(__file__).parent

_SAMPLES_PER_CHUNK = 1024


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="stdio://", help="unix:// or tcp://")
    parser.add_argument(
        "--espeak-ng-bin",
        help="Path to espeak-ng executable",
    )
    parser.add_argument(
        "--nanotts-bin",
        help="Path to nanotts executable",
    )
    parser.add_argument(
        "--nanotts-lang",
        help="Path to nanotts lang directory (share/pico/lang)",
    )
    parser.add_argument(
        "--flite-bin",
        help="Path to flite executable",
    )
    parser.add_argument(
        "--flite-voices",
        help="Path to flite voices directory (.flitevox files)",
    )
    parser.add_argument(
        "--festival-bin",
        help="Path to text2wave executable",
    )
    parser.add_argument(
        "--marytts-dir",
        help="Path to base MaryTTS directory",
    )
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    tts_systems: Dict[str, TTSBase] = {}

    # espeak-ng
    if (not args.espeak_ng_bin) and shutil.which("espeak-ng"):
        args.espeak_ng_bin = "espeak-ng"

    if args.espeak_ng_bin:
        tts_systems["espeak-ng"] = EspeakTTS(args.espeak_ng_bin)

    # nanoTTS
    if (not args.nanotts_bin) and shutil.which("nanotts"):
        args.nanotts_bin = "nanotts"

    if args.nanotts_bin:
        tts_systems["nanotts"] = NanoTTS(args.nanotts_bin, args.nanotts_lang)

    # flite
    if (not args.flite_bin) and shutil.which("flite"):
        args.flite_bin = "flite"

    if args.flite_bin:
        tts_systems["flite"] = FliteTTS(args.flite_bin, args.flite_voices)

    # festival
    if (not args.festival_bin) and shutil.which("text2wave"):
        args.festival_bin = "text2wave"

    if args.festival_bin:
        tts_systems["festival"] = FestivalTTS(args.festival_bin)

    # MaryTTS
    if args.marytts_dir:
        if shutil.which("java"):
            tts_systems["marytts"] = MaryTTS(args.marytts_dir)
        else:
            _LOGGER.warning("Java is not installed. MaryTTS disabled.")

    _LOGGER.info("Loaded TTS systems: %s", sorted(list(tts_systems.keys())))

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="openTTS",
                description="A collection of open text-to-speech systems",
                attribution=Attribution(
                    name="synesthesiam",
                    url="https://github.com/synesthesiam/opentts",
                ),
                installed=True,
                version="1.0.0",
                voices=[
                    TtsVoice(
                        name=f"{tts_name}.{voice.id}",
                        description=f"{tts_name} {voice.name}",
                        attribution=tts_system.attribution,
                        installed=True,
                        languages=[voice.locale],
                        version=None,
                    )
                    for tts_name, tts_system in tts_systems.items()
                    async for voice in tts_system.voices()
                ],
            )
        ],
    )

    _LOGGER.info("Ready")

    # Start server
    server = AsyncServer.from_uri(args.uri)

    try:
        await server.run(
            partial(
                OpenTTSEventHandler,
                wyoming_info,
                args,
                tts_systems,
            )
        )
    except KeyboardInterrupt:
        pass


# -----------------------------------------------------------------------------


class OpenTTSEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        tts_systems: Dict[str, TTSBase],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.client_id = str(time.monotonic_ns())
        self.tts_systems = tts_systems

        _LOGGER.debug("Client connected: %s", self.client_id)

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info to client: %s", self.client_id)
            return True

        if Synthesize.is_type(event.type):
            tts_name: Optional[str] = None
            voice_id: Optional[str] = None

            synthesize = Synthesize.from_event(event)
            _LOGGER.debug(synthesize)
            if (synthesize.voice is not None) and ("." in synthesize.voice.name):
                tts_name, voice_id = synthesize.voice.name.split(".", maxsplit=1)

            if (not tts_name) or (not voice_id):
                await self.write_event(Error("TTS system or voice not found").event())
                return True

            tts_system = self.tts_systems.get(tts_name)

            if tts_system is None:
                await self.write_event(
                    Error(f"TTS system not found: {tts_system}").event()
                )
                return True

            voice_found = False
            async for voice in tts_system.voices():
                if voice.id == voice_id:
                    voice_found = True
                    break

            if not voice_found:
                await self.write_event(Error(f"Voice not found: {voice_id}").event())
                return True

            wav_bytes = await tts_system.say(synthesize.text, voice_id)
            _LOGGER.debug("Got %s byte(s) of WAV data", len(wav_bytes))
            with io.BytesIO(wav_bytes) as wav_io:
                wav_file: wave.Wave_read = wave.open(wav_io, "rb")
                for wav_event in wav_to_chunks(
                    wav_file,
                    samples_per_chunk=_SAMPLES_PER_CHUNK,
                    start_event=True,
                    stop_event=True,
                ):
                    await self.write_event(wav_event.event())
        else:
            _LOGGER.debug("Unexpected event: type=%s, data=%s", event.type, event.data)

        return True

    async def disconnect(self) -> None:
        _LOGGER.debug("Client disconnected: %s", self.client_id)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
