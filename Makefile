HERE = $(shell pwd)
BIN = $(HERE)/venv/bin
PYTHON = $(BIN)/python3.4

INSTALL = $(BIN)/pip install

SYNCTO_SERVER_URL = https://syncto.stage.mozaws.net:443
SYNCTO_EXISTING_EMAIL =

.PHONY: all test build

all: build test

$(PYTHON):
	$(shell basename $(PYTHON)) -m venv $(VTENV_OPTS) venv
	$(BIN)/pip install requests requests_hawk flake8
	$(BIN)/pip install https://github.com/mozilla/PyFxA/archive/loadtest-tools.zip
	$(BIN)/pip install https://github.com/tarekziade/ailoads/archive/master.zip
build: $(PYTHON)

loadtest.env:
	$(BIN)/fxa-client -c --browserid --audience https://token.stage.mozaws.net/ --prefix syncto --out loadtest.env

refresh:
	@rm -f loadtest.env

setup_random: refresh loadtest.env

setup_existing:
	$(BIN)/fxa-client --browserid --auth "$(SYNCTO_EXISTING_EMAIL)" --env production --out loadtest.env


test: build loadtest.env
	bash -c "source loadtest.env && SYNCTO_SERVER_URL=$(SYNCTO_SERVER_URL) $(BIN)/ailoads -v -d 30"
	$(BIN)/flake8 loadtest.py

test-heavy: build loadtest.env
	bash -c "source loadtest.env && SYNCTO_SERVER_URL=$(SYNCTO_SERVER_URL) $(BIN)/ailoads -v -d 300 -u 10"

clean: refresh
	rm -fr venv/ __pycache__/

docker-build:
	docker build -t syncto/loadtest .

docker-run: loadtest.env
	bash -c "source loadtest.env; docker run -e SYNCTO_DURATION=600 -e SYNCTO_NB_USERS=10 -e SYNCTO_SERVER_URL=$(SYNCTO_SERVER_URL) -e FXA_BROWSERID_ASSERTION=\$${FXA_BROWSERID_ASSERTION} -e FXA_CLIENT_STATE=\$${FXA_CLIENT_STATE} syncto/loadtest"

configure: build loadtest.env
	@bash syncto.tpl

docker-export:
	docker save "syncto/loadtest:latest" | bzip2> syncto-latest.tar.bz2
