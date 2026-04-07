# Rambutan

v1.0.0

Rambutan is a webapp that hooks into the database of a [Lychee](https://github.com/LycheeOrg/Lychee/) server and shows random pictures from it.

## Current Status

* Dockerized - appears [here](https://github.com/adelairdragon/rambutan/pkgs/container/rambutan)
* Tested with SQLite and MySQL, run locally and in docker container.
* Tested up to Lychee v7.5.0

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