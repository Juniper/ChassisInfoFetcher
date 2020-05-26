FROM alpine:3.9

RUN apk add --no-cache build-base python2-dev py-lxml libxslt-dev libxml2-dev curl \
    ca-certificates openssl-dev git py2-pip libffi-dev

WORKDIR /CIF
COPY CIF .

RUN pip install urwid requests junos-eznc \
    git+https://github.com/Juniper/py-space-platform.git@v1.0.0

ENTRYPOINT ["python"]
CMD ["app.py"]
