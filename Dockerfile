FROM debian:bookworm
ARG TARGETARCH
ARG TARGETVARIANT

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

# Needed for festvox packages
RUN echo 'deb http://deb.debian.org/debian bookworm contrib non-free' > /etc/apt/sources.list.d/contrib.list

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
      python3 \
      python3-venv \
      wget \
      espeak-ng \
      espeak-ng-data \
      flite \
      festival \
      festvox-ca-ona-hts \
      festvox-czech-dita \
      festvox-czech-krb \
      festvox-czech-machac \
      festvox-czech-ph \
      festvox-don \
      festvox-en1 \
      festvox-kallpc16k \
      festvox-kdlpc16k \
      festvox-rablpc16k \
      festvox-us1 \
      festvox-us2 \
      festvox-us3 \
      festvox-us-slt-hts \
      festvox-ellpc11k \
      festvox-suopuhe-lj \
      festvox-suopuhe-mv \
      festvox-italp16k \
      festvox-itapc16k \
      festvox-mr-nsk \
      festvox-ru \
      festvox-te-nsk \
      openjdk-17-jre-headless  # marytts

WORKDIR /app

RUN mkdir -p ./local

# Install prebuilt nanoTTS
RUN mkdir -p ./local/nanotts && \
    wget -O - --no-check-certificate \
        "https://github.com/synesthesiam/prebuilt-apps/releases/download/v1.0/nanotts-20200520_${TARGETARCH}${TARGETVARIANT}.tar.gz" | \
        tar -C ./local/nanotts -xzf -

# Festival voices
RUN mkdir -p ./local/festival && \
    wget -O - --no-check-certificate \
        "https://github.com/synesthesiam/opentts/releases/download/v2.1/festival-voices.tar.gz" | \
        tar -C ./local -xzf -

# Flite voices
RUN wget -O - --no-check-certificate \
        "https://github.com/synesthesiam/opentts/releases/download/v2.1/flite-voices.tar.gz" | \
        tar -C ./local -xzf -

# MaryTTS voices
RUN mkdir -p ./local/marytts && \
    wget -O - --no-check-certificate \
        "https://github.com/synesthesiam/opentts/releases/download/v2.1/marytts-voices.tar.gz" | \
        tar -C ./local -xzf -

# Post-installation
RUN cp "./local/festival/ar/languages/language_arabic.scm" \
       "/usr/share/festival/languages/" && \
    mkdir -p "/usr/share/festival/voices/arabic" && \
    cp -r "./local/festival/ar/voices/ara_norm_ziad_hts" "/usr/share/festival/voices/arabic/"

# Python module
COPY requirements.txt ./
RUN python3 -m venv .venv && \
    .venv/bin/pip3 install --upgrade pip && \
    .venv/bin/pip3 install --upgrade wheel setuptools

RUN .venv/bin/pip3 install -r requirements.txt

COPY wyoming_opentts/ ./wyoming_opentts/
COPY docker/run.sh ./

EXPOSE 10200

ENTRYPOINT ["bash", "/app/run.sh"]

# -----------------------------------------------------------------------------
