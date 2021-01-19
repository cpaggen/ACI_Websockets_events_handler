# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt --proxy proxy.esl.cisco.com:80

# copy the content of the local src directory to the working directory
COPY aci-src/ .

# command to run on container start
ENTRYPOINT ["python","./events.py"]
