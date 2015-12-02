HERE = $(shell pwd)
BIN = $(HERE)/venv/bin
PYTHON = $(BIN)/python3.4

INSTALL = $(BIN)/pip install

SYNCTO_FXA_USER_SALT = 9aDdRQoLQBPsThVew-GZM_7PrJw_wf0skON0t4RjTDWewmu9
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
	fxa-client -c --browserid --audience https://token.stage.mozaws.net/ --prefix syncto --out loadtest.env
setup_random: loadtest.env

setup_existing:
	fxa-client --browserid --auth "$(SYNCTO_EXISTING_EMAIL)" --account-server https://api.accounts.firefox.com/v1 --out loadtest.env


test: build loadtest.env
	bash -c "source loadtest.env && SYNCTO_SERVER_URL=$(SYNCTO_SERVER_URL) $(BIN)/ailoads -v -d 30"
	$(BIN)/flake8 loadtest.py

test-heavy: build loadtest.env
	bash -c "source loadtest.env && SYNCTO_SERVER_URL=$(SYNCTO_SERVER_URL) $(BIN)/ailoads -v -d 300 -u 10"

clean:
	rm -fr venv/ __pycache__/

docker-build:
	docker build -t syncto/loadtest .

docker-run: loadtest.env
	bash -c "source loadtest.env && docker run -e SYNCTO_DURATION=600 -e SYNCTO_NB_USERS=10 -e SYNCTO_SERVER_URL=$(SYNCTO_SERVER_URL) -e FXA_BROWSERID_ASSERTION=$${FXA_BROWSERID_ASSERTION} -e FXA_CLIENT_STATE=$${FXA_CLIENT_STATE} syncto/loadtest"
