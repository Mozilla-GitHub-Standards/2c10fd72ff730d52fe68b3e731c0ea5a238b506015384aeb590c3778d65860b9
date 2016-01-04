FROM python:3.4-wheezy
MAINTAINER Mozilla Cloud Services

RUN echo "deb http://ftp.debian.org/debian sid main" >> /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-virtualenv
RUN apt-get install -y git
RUN apt-get install -y wget
RUN apt-get install -y python3-dev

# Adding syncto user
RUN adduser --system syncto
USER syncto

# deploying the ailoads-syncto project
RUN git clone https://github.com/mozilla-services/ailoads-syncto /home/syncto/ailoads-syncto
RUN cd /home/syncto/ailoads-syncto; make build

# run the test
CMD cd /home/syncto/ailoads-syncto; venv/bin/ailoads -v -d $SYNCTO_DURATION -u $SYNCTO_NB_USERS
