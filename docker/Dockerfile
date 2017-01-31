FROM juniper/pyez

RUN pip install urwid
RUN pip install requests
RUN apk add --update git 
RUN git clone https://github.com/Juniper/py-space-platform.git
RUN pip install ./py-space-platform
RUN git clone https://git.juniper.net/mgospodinov/ChassisInfoFetcher2.0.git