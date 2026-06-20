# ScummVM Linux 開發 build 環境(供本機驗證 AGS engine + CJK patch)
# Android / macOS 正式打包走 GitHub Actions,不在此 image。
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential git pkg-config \
        libsdl2-dev libsdl2-net-dev \
        zlib1g-dev libpng-dev libjpeg-turbo8-dev \
        libfreetype-dev libfaad-dev libmad0-dev libvorbis-dev \
        libflac-dev libmpeg2-4-dev libtheora-dev libfluidsynth-dev \
        libgtk-3-dev liba52-0.7.4-dev \
        ca-certificates xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
CMD ["/bin/bash"]
