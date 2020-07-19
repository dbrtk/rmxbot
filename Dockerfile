FROM ubuntu:19.10

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

# name the portage image
# FROM gentoo/portage:latest as portage
#
# # image is based on stage3-amd64
# FROM gentoo/stage3-amd64:latest
#
# # copy the entire portage volume in
# COPY --from=portage /var/db/repos/gentoo /var/db/repos/gentoo
#
# # RUN emerge --update --newuse --deep @world
#
# RUN emerge -qv www-servers/nginx dev-python/pip dev-python/virtualenv

# RUN useradd -ms /bin/bash rmx
# USER rmx


COPY rmxbot /opt/program/rmxbot
COPY conf/nginx/nginx.conf /opt/program
COPY serve /opt/program
COPY requirements.txt /opt/program

COPY templates /opt/program/templates

COPY celery.sh /opt/program
COPY celery_worker.py /opt/program

RUN python3 --version

RUN python3 -m pip install --upgrade pip && \
	python3 -m pip install -r /opt/program/requirements.txt && \
	python3 -m pip list

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

# ENV PYTHONUNBUFFERED=TRUE
# ENV PYTHONDONTWRITEBYTECODE=TRUE
# ENV PATH='/opt/program:${PATH}'


# Make port 8000 available to the world outside this container
# EXPOSE 8000

# ENTRYPOINT ["serve"]

