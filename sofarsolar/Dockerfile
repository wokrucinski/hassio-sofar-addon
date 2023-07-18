FROM python:3.10

ADD inverter /inverter
ADD run.sh /

RUN apk add sudo
RUN sudo pip install paho-mqtt anyconfig

CMD [ "/run.sh" ]
