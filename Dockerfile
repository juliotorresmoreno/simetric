
FROM ubuntu:20.04

RUN apt update -y && apt dist-upgrade -y
RUN apt install python3 python3-pip libmysqlclient-dev -y
RUN adduser simetric --gecos "" --home /var/lib/simetric --disabled-password --disabled-login
ADD . /opt/simetric
WORKDIR /opt/simetric
RUN pip3 install -r requirements.txt
USER simetric

ENTRYPOINT [ "/opt/simetric/entrypoint.sh" ]
