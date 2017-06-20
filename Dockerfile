FROM juniper/pyez

RUN pip install --upgrade pip

RUN apk update && apk add git \
    && pip install urwid \
    && pip install requests \
    && pip install git+https://github.com/Juniper/py-space-platform.git@v1.0.0

COPY CIF .


CMD “/bin/bash”
CMD “CD CIF”
CMD "python" "./app.py"
