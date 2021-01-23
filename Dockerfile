FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends \
	build-essential \
	python3-dev \
	python3-venv \
	python3-setuptools \
	python3-pip \
	nginx \
	ca-certificates \
    && apt-get -y autoremove && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

COPY rmxbot /opt/program/rmxbot
COPY conf/nginx/nginx.conf /opt/program
COPY serve /opt/program
COPY requirements.txt /opt/program

COPY templates /opt/program/templates

COPY celery.sh /opt/program
COPY celery_worker.py /opt/program

RUN python3 -m pip install --upgrade pip && \
	python3 -m pip install -r /opt/program/requirements.txt

# chmod perms on executables
RUN chmod +x /opt/program/serve
RUN ln -s /opt/program/serve /usr/local/bin/serve


WORKDIR /opt/program


# environment variables

# the endpoint for extractxt
ENV EXTRACTXT_ENDPOINT 'http://extractxt:8003'

# the data root
ENV DATA_ROOT '/data'
# the tmp dir for rmxbot
ENV TMP_DATA_DIR '/tmp'

ENV TEMPLATES_FOLDER '/opt/program/templates'

ENV STATIC_FOLDER '/var/www/rmx'

