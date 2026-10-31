# syntax=docker/dockerfile:1
# Code only. Content (profile/jobs/cv/prep/offers/sync) lives in the /data volume
# and is seeded on first run — never baked into the image.
FROM python:3.13-slim

ARG UID=1000
ARG GID=1000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    JC_DATA=/data \
    JC_HOST=0.0.0.0 \
    JC_PORT=8765

RUN groupadd -g "$GID" app && useradd -u "$UID" -g app -m app

WORKDIR /app
COPY tools/ /app/tools/
COPY profile.example.md /app/seeds/profile.example.md
COPY jobs/_example.md /app/seeds/jobs/_example.md
COPY cv/_example-en.md /app/seeds/cv/_example-en.md
COPY prep/_example.md /app/seeds/prep/_example.md
COPY offers/_example.md /app/seeds/offers/_example.md
COPY sync/_example.md /app/seeds/sync/_example.md
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

VOLUME /data
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python3 -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8765/api/jobs')" || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["serve"]
