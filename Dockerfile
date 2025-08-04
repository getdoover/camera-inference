FROM spaneng/doover_device_base AS base_image
LABEL com.doover.app="true"
LABEL com.doover.managed="true"
HEALTHCHECK --interval=30s --timeout=2s --start-period=5s CMD curl -f "127.0.0.1:$HEALTHCHECK_PORT" || exit 1

## FIRST STAGE ##
FROM base_image AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# give the app access to our pipenv installed packages
RUN uv venv --system-site-packages
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


## SECOND STAGE ##
FROM base_image AS final_image

# Install YOLO, OpenCV, and WebRTC dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \

#     libsm6 \
#     libxext6 \
#     libxrender-dev \
    ffmpeg 
#     libavcodec-dev \
#     libavformat-dev \
#     libavutil-dev \
#     libswscale-dev \
#     libavresample-dev \
#     libavfilter-dev \
#     libgstreamer1.0-dev \
#     libgstreamer-plugins-base1.0-dev \
#     libgstreamer-plugins-bad1.0-dev \
#     gstreamer1.0-plugins-base \
#     gstreamer1.0-plugins-good \
#     gstreamer1.0-plugins-bad \
#     gstreamer1.0-plugins-ugly \
#     gstreamer1.0-libav \
#     gstreamer1.0-tools \
#     gstreamer1.0-x \
#     gstreamer1.0-alsa \
#     gstreamer1.0-gl \
#     gstreamer1.0-gtk3 \
#     gstreamer1.0-qt5 \
#     gstreamer1.0-pulseaudio \
#     && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["doover-app-run"]
