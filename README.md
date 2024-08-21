# Rambutan

v0.0.1

Rambutan is a webapp that hooks into the database of a [Lychee](https://github.com/LycheeOrg/Lychee/) server and shows random pictures from it.

## Current Status

* Recently dockerized!
* Tested with SQLite, run locally and in docker container.
* Up next: Testing with MySQL

## How to Run

Before running, you will need to create a `config.toml` file. You can use `config_example.toml` as a reference.

### Running Locally

1. Create `config.toml` file
2. Install dependencies with `pip install -r requirements.txt` (or equivalent for your Python package manager of choice)
3. Run the app with `python app.py`

### Running in Docker Container

1. Create `config.toml` file
2. Build the docker container with `sudo docker build -t rambutan .`
3. Run the container with `sudo docker run -d -p 8000:8000 -v ${PWD}/config.toml:/app/config.toml:ro -v ${PWD}/adelair_example.db:/app/instance/adelair_example.db rambutan`