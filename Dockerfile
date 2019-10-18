FROM daocloud.io/ubuntu:trusty
MAINTAINER water-law <dockerwaterlaw@daocloud.io>
RUN apt-get update && \
	apt-get install -y python3 \
						python3-dev \
						python3-pip \
	&& apt-get clean \
	&& apt-get autoclean \
	&& rm -rf /var/lib/apt/lists/*