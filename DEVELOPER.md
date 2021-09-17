# Developer Notes

The following document will explain how to configure your environment locally, run the app, and run the tests. This should help with meaningful contribution to the project and more reliable pull request approvals.

## Overview

This project consists of two primary parts: a Vue.js [frontend](#frontend) and a FastAPI [backend](#backend).

### Dependency Installation

There are two different `package.json` files which will need to have dependencies installed. You should install a modern version of [node](https://nodejs.org/en/download/) (14+) and the latest version of [yarn v1](https://classic.yarnpkg.com/en/docs/install#windows-stable) prior to running the following commands.

```bash
# double check node is installed
node --version

# double check yarn is installed
yarn --version

# install node packages to allow project-wide commit linting and other hooks
cd c:/git/sfm
yarn install # in the root directory

# install packages for the frontend
cd src/frontend
yarn install
```

> Make sure you have the following settings in your VSCode settings.json file to allow auto lint on save.

```json
"editor.codeActionsOnSave": {
        "source.fixAll": true,
    }
```

Prior to committing you'll also need to install `pre-commit` in your python environment which will enable the `black` fomatter for python. On each committhe pre-commit hooks will automatically:

- Format any python files with black
- Format any javascript or similar files with prettier
- lint any commit messages and enforce the commit standard outlined below.

### Commits & Contributions

This is the standard we use for commits: [Commit Standard](https://www.conventionalcommits.org/en/v1.0.0/)

```bash
git add xxx  # stage your files
git commit -m "foo bar"  # this will fail on auto-commit-lint
git commit -m "feat(foo): bar stuff & things"  # this will pass
yarn commit  # interactive commit messages
```

The following are good examples of commit messages:

`style(footer): remove blue border surrounding the right side text box`

`refactor(button props): change the button props to allow a text value to be passed in`

### Changelog Update

We use [standard version](https://github.com/conventional-changelog/standard-version) for our auto-changelog. It should be run after changes to the `main` branch usually by whoever accepts a pull request.

```bash
yarn release  # after commiting, from the project root
```

## Frontend

### Clone the Project

Clone the project from GitHub, perferably using [ssh]() authentication with the following commands

```bash
# move to a folder called `git` <- not mandatory, but good practice
cd c:/git

# clone
git clone git@github.com:rropen/SFM.git
```

For local development, the frontend just runs on your machine. After installing the dependencies in `src/frontend` you can run it with the commands below. This is the easiest way to work on this service.

### Running Locally

```bash
# from the root/src/frontend folder
yarn serve # served with vite - app available at http://localhost:3000 by default
```

### Build for Production

```bash
yarn build
```

### End-To-End Testing

You can run the E2E tests in one of two ways:

**In a Terminal**

```bash
# navigate to the frontend folder
cd /src/frontend

# run the command
yarn cy
```

**Interactively in a Browser**

```bash
# navigate to the frontend folder
cd /src/frontend

# run the command
yarn cy-open
```

### Component Testing

You can run the component tests in one of two ways:

**In a Terminal**

```bash
# navigate to the frontend folder
cd /src/frontend

# run the command
yarn cy-ct
```

**Interactively in a Browser**

```bash
# navigate to the frontend folder
cd /src/frontend

# run the command
yarn cy-open-ct
```

## Backend

For local development, the backend should be run in docker. You'll need to do one step before building the container. Make sure you install a version of [Docker](https://www.docker.com/products/personal) for your machine.

```bash
# Navigate to the backend service location
cd src/backend

# make a new .env file
cp .env.example .env
```

The example .env file should already be sufficient for local development with only the two environment variables. The .env file you use for your development shouldn't be committed to source code. This should be taken care of automatically by the .gitignore file.

### Build the docker image

```bash
# Move to the docker-compose context where the docker-compose files are located
cd src

# Build the container
docker-compose -f docker-compose.yml -f local-docker-compose.yml build

# Run the container in detached mode to return your command prompt
docker-compose -f docker-compose.yml -f local-docker-compose.yml up -d backend
```

<!--
```
# Check the status of your container.
docker ps

# Attach to the log output from the container (ctrl+c to escape)
docker compose logs -f

# Create & migrate local database
docker exec -it src_backend_1 bash
alembic upgrade head
exit
```
-->

### Run Locally

If you want to install the dependencies and run the backend project locally for some reason, use [pdm](https://pdm.fming.dev/usage/project.html). PDM uses the `pyproject.toml` file to store the project requirements instead of the `requirements.txt` like most people are used to. It's actually a much nicer system that lets you avoid the virtual environment messes of the past. But it's a bit different and can take some getting used to.

> You'll need python 3.8 or higher installed on your machine to use the packages as specified.

```bash
# verify you have pdm installed
pdm --version

# if you don't, install it
pip install pdm

cd src/backend
pdm install
```

To run the project just run `pdm run uvicorn main:app --workers 4 --host 0.0.0.0 --port 8181 --reload`

Your backend container should be running at `http://localhost:8181/docs` on your local machine.

### Clearing the database

To clear the database and prepare it for seeding mock data, simply navigate to the bottom of the SwaggerUI docs located at `http://localhost:8181/docs` and execute the `/clear_local_db` endpoint. To do this programmatically, send a DELETE request to `http://localhost:8181/utilities/clear_local_db`

### Seeding the Database

To help with local development amongst teams, an API endpoint was created to initialize the database with a standardized set of mock data. _This will require a cleared database to work._ You can access this endpoint either at the bottom of the SwaggerUI docs located at `http://localhost:8181/docs` or by sending a POST request to `http://localhost:8181/utilities/populate_mock_data`

### Unit Testing

To run the backend unit tests:

```bash
# Move to the tests directory
cd src/backend/tests

# Run pytest
pdm run pytest
```

Note: The command line options for pytest are configured in the `pytest.ini` file so you don't need to add them when running the command.

Code coverage will be displayed if all tests pass.
