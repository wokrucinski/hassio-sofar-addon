FROM python:3.10

ADD inverter /inverter
ADD run.sh /

RUN pip3 install paho-mqtt anyconfig

CMD [ "/run.sh" ]
