# ailoads-syncto

Syncto loadtest based on ailoads


## Generate your credentials

### For stage

   make setup_random

### For production

   make setup_existing -e SYNCTO_EXISTING_EMAIL=test-account-email@example.com


## How to run the loadtest?

    make test


## How to run a longer loadtest with multiple users?

    make test-heavy


## How to build the docker image?

    make docker-build


## How to run the docker image?

    make docker-run


## How to clean the repository?

    make clean
