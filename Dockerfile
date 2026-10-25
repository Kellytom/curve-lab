# Build the shared library, then keep only the runtime pieces.
FROM debian:bookworm-slim AS native

RUN apt-get update \
    && apt-get install -y --no-install-recommends clang \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .
ENV CXX=clang++
RUN bash scripts/build-native.sh

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=native /src/build/libclothoidlab.so /app/build/libclothoidlab.so
COPY clothoid_lab /app/clothoid_lab
COPY web /app/web
COPY out/caps /app/out/caps

ENV HOST=0.0.0.0 \
    PORT=8080 \
    PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python", "web/server.py"]
