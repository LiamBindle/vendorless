FROM alpine:3.22
WORKDIR /data
RUN apk add --no-cache poetry

COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]