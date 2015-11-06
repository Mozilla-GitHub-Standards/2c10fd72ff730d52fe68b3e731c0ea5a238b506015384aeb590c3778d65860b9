HERE = $(shell pwd)
BIN = $(HERE)/venv/bin
PYTHON = $(BIN)/python3.4

INSTALL = $(BIN)/pip install

SYNCTO_FXA_USER_SALT = 9aDdRQoLQBPsThVew-GZM_7PrJw_wf0skON0t4RjTDWewmu9

.PHONY: all test build

all: build test

$(PYTHON):
	$(shell basename $(PYTHON)) -m venv $(VTENV_OPTS) venv
	$(BIN)/pip install requests requests_hawk PyFxA flake8
	$(BIN)/pip install https://github.com/tarekziade/ailoads/archive/master.zip
build: $(PYTHON)

init:
	sed -i "s/SYNCTO_FXA_USER_SALT=[a-zA-Z0-9_-]*/SYNCTO_FXA_USER_SALT=`python -c 'import os, base64; print(base64.urlsafe_b64encode(os.urandom(36)))'`/g" syncto.json

test: build
	SYNCTO_FXA_USER_SALT=$(SYNCTO_FXA_USER_SALT) $(BIN)/ailoads -v -d 30
	$(BIN)/flake8 loadtest.py

clean:
	rm -fr venv/ __pycache__/

docker-build:
	docker build -t syncto/loadtest .

docker-run:
	docker run -e SYNCTO_DURATION=30 -e SYNCTO_NB_USERS=4 syncto/loadtest
