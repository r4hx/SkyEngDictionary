ARG CACHE_FULL

FROM ${CACHE_FULL}/python:3.10.12 as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/
COPY requirements.txt /app/
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt 

FROM ${CACHE_FULL}/python:3.10.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/
COPY --from=builder /root/.local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
RUN useradd skyeng -u 23344 -M --home "/app" -s /bin/false
USER skyeng
COPY --chown=skyeng:skyeng . .