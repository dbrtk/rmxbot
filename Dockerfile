FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN chmod +x /app/run.sh && chmod +x /app/celery.sh

# the endpoint for extractxt
ENV EXTRACTXT_ENDPOINT 'http://extractxt:8003'

# the endpoint for rmxgrep
ENV RMXGREP_ENDPOINT 'http://rmxgrep:8004'

# the data root
ENV DATA_ROOT '/data'
# the tmp dir for rmxbot
ENV TMP_DATA_DIR '/tmp'

# the location of mongodb
ENV MONGODB_LOCATION 'mongodb'
# the name of the database
ENV MONGODB_NAME 'rmx'

# the redis host
ENV BROKER_HOST_NAME 'message_broker'

ENV TEMPLATES_FOLDER '/app/templates'

ENV STATIC_FOLDER '/var/www/rmx'

# Install any needed packages specified in requirements.txt
RUN pip install -U pip && pip install .

# Make port 8000 available to the world outside this container
EXPOSE 8000
