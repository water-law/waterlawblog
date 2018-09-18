FROM daocloud.io/ubuntu:trusty
MAINTAINER water-law <dockerwaterlaw@daocloud.io>
RUN apt-get update && \
	apt-get install -y python3 \
						python3-dev \
						python3-pip \
	&& apt-get clean \
	&& apt-get autoclean \
	&& rm -rf /var/lib/apt/lists/*

RUN pip3 install virtualenv && virtualenv -p /usr/bin/python3 /home/pysp
ADD requirements.txt /tmp/requirements.txt
RUN . /home/pysp/bin/activate && pip3 install -r /tmp/requirements.txt && mkdir -p /home/code
WORKDIR /home/code
