FROM alpine:3.22
WORKDIR /data
RUN apk add --no-cache poetry

RUN echo "#!/bin/sh" > /entrypoint.sh && \
    echo "poetry install" >> /entrypoint.sh && \
    echo 'poetry run vl "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]