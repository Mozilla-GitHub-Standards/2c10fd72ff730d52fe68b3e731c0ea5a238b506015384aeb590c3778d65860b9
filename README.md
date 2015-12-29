# ailoads-syncto

Syncto loadtest based on ailoads


## How to run the loadtest?

### For stage

   make setup_random test

or for a longer one:

   make setup_random test-heavy

### For production

   make setup_existing -e SYNCTO_EXISTING_EMAIL=test-account-email@example.com
   make test -e SYNCTO_SERVER_URL=https://syncto.dev.mozaws.net:443

or all at once:

   make setup_existing test -e \
       SYNCTO_EXISTING_EMAIL=test-account-email@example.com \
       SYNCTO_SERVER_URL=https://syncto.dev.mozaws.net:443


## How to build the docker image?

    make docker-build


## How to run the docker image?

    make docker-run


## How to clean the repository?

    make clean
