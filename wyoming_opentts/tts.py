"""Text to speech wrappers for OpenTTS"""
import asyncio
import logging
import shlex
import shutil
import tempfile
from abc import ABCMeta, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union
from zipfile import ZipFile

from wyoming.info import Attribution

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


@dataclass
class Voice:
    """Single TTS voice."""

    id: str
    name: str
    gender: str
    language: str
    locale: str
    tag: Optional[Dict[str, Any]] = None
    multispeaker: bool = False
    speakers: Optional[Dict[str, int]] = None


VoicesIterable = AsyncGenerator[Voice, None]


class TTSBase(metaclass=ABCMeta):
    """Base class of TTS systems."""

    @property
    @abstractmethod
    def attribution(self) -> Attribution:
        pass

    async def voices(self) -> VoicesIterable:
        """Get list of available voices."""
        yield Voice("", "", "", "", "")

    async def say(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Speak text as WAV."""
        return bytes()


# -----------------------------------------------------------------------------


class EspeakTTS(TTSBase):
    """Wraps eSpeak (http://espeak.sourceforge.net)"""

    def __init__(self, bin_path: Union[str, Path]) -> None:
        self.bin_path = str(bin_path)

    @property
    def attribution(self) -> Attribution:
        return Attribution(name="espeak-ng", url="http://espeak.sourceforge.net")

    async def voices(self) -> VoicesIterable:
        """Get list of available voices."""
        espeak_cmd = [self.bin_path, "--voices"]
        _LOGGER.debug(espeak_cmd)

        proc = await asyncio.create_subprocess_exec(
            *espeak_cmd, stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()

        voices_lines = stdout.decode().splitlines()
        first_line = True
        for line in voices_lines:
            if first_line:
                first_line = False
                continue

            parts = line.split()
            locale = parts[1]
            language = locale.split("-", maxsplit=1)[0]

            yield Voice(
                id=parts[1],
                gender=parts[2][-1],
                name=parts[3],
                locale=locale,
                language=language,
            )

    async def say(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Speak text as WAV."""
        espeak_cmd = [
            self.bin_path,
            "-v",
            shlex.quote(str(voice_id)),
            "--stdout",
            shlex.quote(text),
        ]
        _LOGGER.debug(espeak_cmd)

        proc = await asyncio.create_subprocess_exec(
            *espeak_cmd, stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout


# -----------------------------------------------------------------------------


class FliteTTS(TTSBase):
    """Wraps flite (http://www.festvox.org/flite)"""

    def __init__(
        self, bin_path: Union[str, Path], voice_dir: Optional[Union[str, Path]] = None
    ):
        self.bin_path = str(bin_path)
        self.voice_dir = Path(voice_dir) if voice_dir else None
        self.voice_id_map = {
            "mycroft_voice_4_0": "mycroft_voice_4.0",
        }

    @property
    def attribution(self) -> Attribution:
        return Attribution(name="CMU", url="http://www.festvox.org/flite")

    async def voices(self) -> VoicesIterable:
        """Get list of available voices."""
        if self.voice_dir is None:
            # Default voices
            flite_voices = [
                Voice(
                    id="awb",
                    name="awb",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="kal",
                    name="kal",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="kal16",
                    name="kal16",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="rms",
                    name="rms",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="slt",
                    name="slt",
                    gender="F",
                    locale="en-us",
                    language="en",
                ),
            ]
            for voice in flite_voices:
                yield voice
        else:
            flite_voices = [
                # English
                Voice(
                    id="cmu_us_aew",
                    name="cmu_us_aew",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_ahw",
                    name="cmu_us_ahw",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_aup",
                    name="cmu_us_aup",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_awb",
                    name="cmu_us_awb",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_axb",
                    name="cmu_us_axb",
                    gender="F",
                    locale="en-in",
                    language="en",
                ),
                Voice(
                    id="cmu_us_bdl",
                    name="cmu_us_bdl",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_clb",
                    name="cmu_us_clb",
                    gender="F",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_eey",
                    name="cmu_us_eey",
                    gender="F",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_fem",
                    name="cmu_us_fem",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_gka",
                    name="cmu_us_gka",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_jmk",
                    name="cmu_us_jmk",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_ksp",
                    name="cmu_us_ksp",
                    gender="M",
                    locale="en-in",
                    language="en",
                ),
                Voice(
                    id="cmu_us_ljm",
                    name="cmu_us_ljm",
                    gender="F",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_lnh",
                    name="cmu_us_lnh",
                    gender="F",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_rms",
                    name="cmu_us_rms",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_rxr",
                    name="cmu_us_rxr",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="cmu_us_slp",
                    name="cmu_us_slp",
                    gender="F",
                    locale="en-in",
                    language="en",
                ),
                Voice(
                    id="cmu_us_slt",
                    name="cmu_us_slt",
                    gender="F",
                    locale="en-us",
                    language="en",
                ),
                Voice(
                    id="mycroft_voice_4_0",
                    name="mycroft_voice_4_0",
                    gender="M",
                    locale="en-us",
                    language="en",
                ),
                # Indic
                Voice(
                    id="cmu_indic_hin_ab",
                    name="cmu_indic_hin_ab",
                    gender="F",
                    locale="hi-in",
                    language="hi",
                ),
                Voice(
                    id="cmu_indic_ben_rm",
                    name="cmu_indic_ben_rm",
                    gender="F",
                    locale="bn-in",
                    language="bn",
                ),
                Voice(
                    id="cmu_indic_guj_ad",
                    name="cmu_indic_guj_ad",
                    gender="F",
                    locale="gu-in",
                    language="gu",
                ),
                Voice(
                    id="cmu_indic_guj_dp",
                    name="cmu_indic_guj_dp",
                    gender="F",
                    locale="gu-in",
                    language="gu",
                ),
                Voice(
                    id="cmu_indic_guj_kt",
                    name="cmu_indic_guj_kt",
                    gender="F",
                    locale="gu-in",
                    language="gu",
                ),
                Voice(
                    id="cmu_indic_kan_plv",
                    name="cmu_indic_kan_plv",
                    gender="F",
                    locale="kn-in",
                    language="kn",
                ),
                Voice(
                    id="cmu_indic_mar_aup",
                    name="cmu_indic_mar_aup",
                    gender="F",
                    locale="mr-in",
                    language="mr",
                ),
                Voice(
                    id="cmu_indic_mar_slp",
                    name="cmu_indic_mar_slp",
                    gender="F",
                    locale="mr-in",
                    language="mr",
                ),
                Voice(
                    id="cmu_indic_pan_amp",
                    name="cmu_indic_pan_amp",
                    gender="F",
                    locale="pa-in",
                    language="pa",
                ),
                Voice(
                    id="cmu_indic_tam_sdr",
                    name="cmu_indic_tam_sdr",
                    gender="F",
                    locale="ta-in",
                    language="ta",
                ),
                Voice(
                    id="cmu_indic_tel_kpn",
                    name="cmu_indic_tel_kpn",
                    gender="F",
                    locale="te-in",
                    language="te",
                ),
                Voice(
                    id="cmu_indic_tel_sk",
                    name="cmu_indic_tel_sk",
                    gender="F",
                    locale="te-in",
                    language="te",
                ),
                Voice(
                    id="cmu_indic_tel_ss",
                    name="cmu_indic_tel_ss",
                    gender="F",
                    locale="te-in",
                    language="te",
                ),
            ]

            for voice in flite_voices:
                voice_id = self.voice_id_map.get(voice.id, voice.id)
                voice_path = self.voice_dir / f"{voice_id}.flitevox"
                if voice_path.is_file():
                    yield voice

    async def say(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Speak text as WAV."""
        voice_id = self.voice_id_map.get(voice_id, voice_id)
        flite_cmd = [
            "flite",
            "-o",
            "/dev/stdout",
            "-t",
            shlex.quote(text),
        ]

        if self.voice_dir is None:
            flite_cmd.extend(["-voice", voice_id])
        else:
            flite_cmd.extend(
                ["-voice", shlex.quote(str(self.voice_dir / f"{voice_id}.flitevox"))]
            )

        _LOGGER.debug(flite_cmd)

        proc = await asyncio.create_subprocess_exec(
            *flite_cmd, stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout


# -----------------------------------------------------------------------------


class FestivalTTS(TTSBase):
    """Wraps festival (http://www.cstr.ed.ac.uk/projects/festival/)"""

    # Single byte text encodings for specific languages.
    # See https://en.wikipedia.org/wiki/ISO/IEC_8859
    #
    # Some encodings differ from linked article (part 1 is missing relevant
    # symbols).
    LANGUAGE_ENCODINGS = {
        "en": "iso-8859-1",
        "ru": "iso-8859-1",  # Russian is transliterated below
        "es": "iso-8859-15",  # Differs from linked article
        "ca": "iso-8859-15",  # Differs from linked article
        "cs": "iso-8859-2",
        "fi": "iso-8859-15",  # Differs from linked article
        "ar": "utf-8",
    }

    FESTIVAL_VOICES = [
        # English
        Voice(
            id="us1_mbrola",
            name="us1_mbrola",
            gender="F",
            locale="en-us",
            language="en",
        ),
        Voice(
            id="us2_mbrola",
            name="us2_mbrola",
            gender="M",
            locale="en-us",
            language="en",
        ),
        Voice(
            id="us3_mbrola",
            name="us3_mbrola",
            gender="M",
            locale="en-us",
            language="en",
        ),
        Voice(
            id="rab_diphone",
            name="rab_diphone",
            gender="M",
            locale="en-gb",
            language="en",
        ),
        Voice(
            id="en1_mbrola",
            name="en1_mbrola",
            gender="M",
            locale="en-us",
            language="en",
        ),
        Voice(
            id="ked_diphone",
            name="ked_diphone",
            gender="M",
            locale="en-us",
            language="en",
        ),
        Voice(
            id="kal_diphone",
            name="kal_diphone",
            gender="M",
            locale="en-us",
            language="en",
        ),
        Voice(
            id="cmu_us_slt_arctic_hts",
            name="cmu_us_slt_arctic_hts",
            gender="F",
            locale="en-us",
            language="en",
        ),
        # Russian
        Voice(
            id="msu_ru_nsh_clunits",
            name="msu_ru_nsh_clunits",
            gender="M",
            locale="ru-ru",
            language="ru",
        ),
        # Spanish
        Voice(
            id="el_diphone",
            name="el_diphone",
            gender="M",
            locale="es-es",
            language="es",
        ),
        # Catalan
        Voice(
            id="upc_ca_ona_hts",
            name="upc_ca_ona_hts",
            gender="F",
            locale="ca-es",
            language="ca",
        ),
        # Czech
        Voice(
            id="czech_dita",
            name="czech_dita",
            gender="F",
            locale="cs-cz",
            language="cs",
        ),
        Voice(
            id="czech_machac",
            name="czech_machac",
            gender="M",
            locale="cs-cz",
            language="cs",
        ),
        Voice(
            id="czech_ph", name="czech_ph", gender="M", locale="cs-cz", language="cs"
        ),
        Voice(
            id="czech_krb", name="czech_krb", gender="F", locale="cs-cz", language="cs"
        ),
        # Finnish
        Voice(
            id="suo_fi_lj_diphone",
            name="suo_fi_lj_diphone",
            gender="F",
            locale="fi-fi",
            language="fi",
        ),
        Voice(
            id="hy_fi_mv_diphone",
            name="hy_fi_mv_diphone",
            gender="M",
            locale="fi-fi",
            language="fi",
        ),
        # Telugu
        Voice(
            id="telugu_NSK_diphone",
            name="telugu_NSK_diphone",
            gender="M",
            locale="te-in",
            language="te",
        ),
        # Marathi
        Voice(
            id="marathi_NSK_diphone",
            name="marathi_NSK_diphone",
            gender="M",
            locale="mr-in",
            language="mr",
        ),
        # Hindi
        Voice(
            id="hindi_NSK_diphone",
            name="hindi_NSK_diphone",
            gender="M",
            locale="hi-in",
            language="hi",
        ),
        # Italian
        Voice(
            id="lp_diphone",
            name="lp_diphone",
            gender="F",
            locale="it-it",
            language="it",
        ),
        Voice(
            id="pc_diphone",
            name="pc_diphone",
            gender="M",
            locale="it-it",
            language="it",
        ),
        # Arabic
        Voice(
            id="ara_norm_ziad_hts",
            name="ara_norm_ziad_hts",
            gender="M",
            locale="ar",
            language="ar",
        ),
    ]

    def __init__(self, bin_path: Union[str, Path]) -> None:
        self.bin_path = str(bin_path)

        self._voice_by_id = {v.id: v for v in FestivalTTS.FESTIVAL_VOICES}

    @property
    def attribution(self) -> Attribution:
        return Attribution(
            name="CSTR", url="http://www.cstr.ed.ac.uk/projects/festival/"
        )

    async def voices(self) -> VoicesIterable:
        """Get list of available voices."""
        available_voices: Set[str] = set()

        if shutil.which("festival"):
            try:
                proc = await asyncio.create_subprocess_exec(
                    "festival",
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                )

                list_command = "(print (voice.list))"
                proc_stdout, _ = await proc.communicate(input=list_command.encode())
                list_result = proc_stdout.decode()

                # (voice1 voice2 ...)
                available_voices = set(list_result[1:-2].split())
                _LOGGER.debug("Festival voices: %s", available_voices)
            except Exception:
                _LOGGER.exception("Failed to get festival voices")

        for voice in FestivalTTS.FESTIVAL_VOICES:
            if (not available_voices) or (voice.id in available_voices):
                yield voice

    async def say(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Speak text as WAV."""
        # Default to part 15 encoding to handle "special" characters.
        # See https://www.web3.lu/character-encoding-for-festival-tts-files/
        encoding = "iso-8859-15"

        # Look up encoding by language
        voice = self._voice_by_id.get(voice_id)
        if voice:
            encoding = FestivalTTS.LANGUAGE_ENCODINGS.get(voice.language, encoding)

            if voice.language == "ar":
                try:
                    # Add diacritics
                    import mishkal.tashkeel

                    vocalizer = getattr(self, "mishkal_vocalizer", None)
                    if vocalizer is None:
                        vocalizer = mishkal.tashkeel.TashkeelClass()
                        setattr(self, "mishkal_vocalizer", vocalizer)

                    text = vocalizer.tashkeel(text)
                    _LOGGER.debug("Added diacritics: %s", text)
                except ImportError:
                    _LOGGER.warning("Missing mishkal package, cannot do diacritizion.")
            elif voice.language == "ru":
                from transliterate import translit

                # Transliterate to Latin script
                text = translit(text, "ru", reversed=True)

        with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
            festival_cmd = [
                self.bin_path,
                "-o",
                wav_file.name,
                "-eval",
                f"(voice_{voice_id})",
            ]
            _LOGGER.debug(festival_cmd)

            proc = await asyncio.create_subprocess_exec(
                *festival_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
            )
            await proc.communicate(input=text.encode(encoding=encoding))

            wav_file.seek(0)
            return wav_file.read()


# -----------------------------------------------------------------------------


class NanoTTS(TTSBase):
    """Wraps nanoTTS (https://github.com/gmn/nanotts)"""

    @property
    def attribution(self) -> Attribution:
        return Attribution(name="gmn", url="https://github.com/gmn/nanotts")

    def __init__(
        self,
        bin_path: Union[str, Path] = "nanotts",
        lang_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.bin_path = str(bin_path)
        self.lang_dir = str(lang_dir) if lang_dir else None

    async def voices(self) -> VoicesIterable:
        """Get list of available voices."""
        nanotts_voices = [
            # English
            Voice(id="en-GB", name="en-GB", gender="F", locale="en-gb", language="en"),
            Voice(id="en-US", name="en-US", gender="F", locale="en-us", language="en"),
            # German
            Voice(id="de-DE", name="de-DE", gender="F", locale="de-de", language="de"),
            # French
            Voice(id="fr-FR", name="fr-FR", gender="F", locale="fr-fr", language="fr"),
            # Spanish
            Voice(id="es-ES", name="es-ES", gender="F", locale="es-es", language="es"),
            # Italian
            Voice(id="it-IT", name="it-IT", gender="F", locale="it-it", language="it"),
        ]

        for voice in nanotts_voices:
            yield voice

    async def say(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Speak text as WAV."""
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
            nanotts_cmd = [
                self.bin_path,
                "-v",
                voice_id,
                "-o",
                shlex.quote(wav_file.name),
            ]
            if self.lang_dir:
                nanotts_cmd.extend(["-l", self.lang_dir])

            _LOGGER.debug(nanotts_cmd)

            proc = await asyncio.create_subprocess_exec(
                *nanotts_cmd, stdin=asyncio.subprocess.PIPE
            )

            await proc.communicate(input=text.encode())

            wav_file.seek(0)
            return wav_file.read()


# -----------------------------------------------------------------------------


class MaryTTS(TTSBase):
    """Wraps a local MaryTTS installation (http://mary.dfki.de)"""

    @property
    def attribution(self) -> Attribution:
        return Attribution(name="dfki", url="http://mary.dfki.de")

    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.voices_dict: Dict[str, Voice] = {}
        self.voice_jars: Dict[str, Path] = {}
        self.voice_proc: Optional["asyncio.subprocess.Process"] = None
        self.proc_voice_id: Optional[str] = None

    async def voices(self) -> VoicesIterable:
        """Get list of available voices."""
        self.maybe_load_voices()

        for voice in self.voices_dict.values():
            yield voice

    async def say(self, text: str, voice_id: str, **kwargs) -> bytes:
        """Speak text as WAV."""
        self.maybe_load_voices()

        if (not self.voice_proc) or (self.proc_voice_id != voice_id):
            if self.voice_proc:
                _LOGGER.debug("Stopping MaryTTS proc (voice=%s)", self.proc_voice_id)

                try:
                    self.voice_proc.terminate()
                    await self.voice_proc.wait()
                    self.voice_proc = None
                except Exception:
                    _LOGGER.exception("marytts")

            # Start new MaryTTS process
            voice = self.voices_dict.get(voice_id)
            assert voice is not None, f"No voice for id {voice_id}"

            voice_jar = self.voice_jars.get(voice_id)
            assert voice_jar is not None, f"No voice jar path for id {voice_id}"

            lang_jar = self.base_dir / "lib" / f"marytts-lang-{voice.language}-5.2.jar"
            assert lang_jar.is_file(), f"Missing language jar at {lang_jar}"

            # Add jars for voice, language, and txt2wav utility
            classpath_jars = [
                voice_jar,
                lang_jar,
                self.base_dir / "lib" / "txt2wav-1.0-SNAPSHOT.jar",
            ]

            # Add MaryTTS and dependencies
            marytts_jars = (self.base_dir / "lib" / "marytts").glob("*.jar")
            classpath_jars.extend(marytts_jars)

            marytts_cmd = [
                "java",
                "-cp",
                ":".join(str(p) for p in classpath_jars),
                "de.dfki.mary.Txt2Wav",
                "-v",
                voice.id,
            ]

            _LOGGER.debug(marytts_cmd)

            self.voice_proc = await asyncio.create_subprocess_exec(
                *marytts_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
            )

            self.proc_voice_id = voice_id

        # ---------------------------------------------------------------------

        assert self.voice_proc is not None

        # Write text
        text_line = text.strip() + "\n"

        assert self.voice_proc.stdin is not None
        self.voice_proc.stdin.write(text_line.encode())
        await self.voice_proc.stdin.drain()

        # Get back size of WAV audio in bytes on first line
        assert self.voice_proc.stdout is not None
        size_line = await self.voice_proc.stdout.readline()
        num_bytes = int(size_line.decode())

        _LOGGER.debug("Reading %s byte(s) of WAV audio...", num_bytes)
        wav_bytes = await self.voice_proc.stdout.readexactly(num_bytes)

        return wav_bytes

    def maybe_load_voices(self):
        """Load MaryTTS voices by opening the jars and finding voice.config"""
        if self.voices_dict:
            # Voices already loaded
            return

        _LOGGER.debug("Loading voices from %s", self.base_dir)
        for voice_jar in self.base_dir.rglob("*.jar"):
            if (not voice_jar.name.startswith("voice-")) or (not voice_jar.is_file()):
                continue

            # Open jar as a zip file
            with ZipFile(voice_jar, "r") as jar_file:
                for jar_entry in jar_file.namelist():
                    if not jar_entry.endswith("/voice.config"):
                        continue

                    # Parse voice.config file for voice info
                    voice_name = ""
                    voice_locale = ""
                    voice_gender = ""

                    with jar_file.open(jar_entry, "r") as config_file:
                        for line_bytes in config_file:
                            try:
                                line = line_bytes.decode().strip()
                                if (not line) or (line.startswith("#")):
                                    continue

                                key, value = line.split("=", maxsplit=1)
                                key = key.strip()
                                value = value.strip()

                                if key == "name":
                                    voice_name = value
                                elif key == "locale":
                                    voice_locale = value
                                elif key.endswith(".gender"):
                                    voice_gender = value
                            except Exception:
                                # Ignore parsing errors
                                pass

                    if voice_name and voice_locale:
                        # Successful parsing
                        voice_lang = voice_locale.split("_", maxsplit=1)[0]

                        self.voice_jars[voice_name] = voice_jar
                        self.voices_dict[voice_name] = Voice(
                            id=voice_name,
                            name=voice_name,
                            locale=voice_locale.lower().replace("_", "-"),
                            language=voice_lang,
                            gender=voice_gender,
                        )

                        _LOGGER.debug(self.voices_dict[voice_name])
