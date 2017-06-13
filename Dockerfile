FROM juniper/pyez

WORKDIR /ChassisInfoFetcher/

ADD requirements.txt requirements.txt
ADD *.py ./
ADD hosts.csv hosts.csv
ADD output output
ADD conf conf

RUN apk update && apk add git \
    && pip install -r requirements.txt \
    && pip install git+https://github.com/Juniper/py-space-platform.git@v1.0.0
    ##&& git clone -b v1.0.0 https://github.com/Juniper/py-space-platform.git \
    ##&& pip install py-space-platform/py-space-platform

RUN chmod a+x *.py

VOLUME $PWD:/ChassisInfoFetcher/

RUN pwd && ls -al

CMD "python" "./app.py"
