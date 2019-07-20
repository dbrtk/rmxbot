# this should use python:3.7
FROM python:3.7

# Creating a user tu run the process
RUN groupadd -r rmxbotuser && useradd -r -g rmxbotuser rmxbotuser

RUN mkdir -p /data/corpus && mkdir /data/upload \
	&& chown -R rmxbotuser:rmxbotuser /data/corpus

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN chown -R rmxbotuser:rmxbotuser /app \
    && chmod +x /app/run.sh \
    && chmod +x /app/celery.sh

# setting up the environment variables for the rmxbot configuration file
ENV RMX_SEARCH_CORPUS_SCRIPT '/opt/rmxgrep/search_corpus.sh'

# the endpoint for extractxt
ENV EXTRACTXT_ENDPOINT 'http://localhost:8003'

# the endpoint for rmxgrep
ENV RMXGREP_ENDPOINT 'http://localhost:8004'

# the data root
ENV DATA_ROOT '/data'
# the tmp dir for rmxbot
ENV TMP_DATA_DIR '/tmp'

# the location of mongodb
ENV MONGODB_LOCATION 'mongodb'

# the redis host
ENV REDIS_HOST_NAME 'redis'

ENV UPLOAD_FOLDER '/data/upload'

ENV TEMPLATES_FOLDER '/app/templates'

ENV STATIC_FOLDER '/var/www/rmx'

# Install any needed packages specified in requirements.txt
RUN pip install -U pip && pip install .

# Make port 8000 available to the world outside this container
EXPOSE 8000

USER rmxbotuser
