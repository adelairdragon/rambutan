# Rambutan

Rambutan is a webapp that hooks into the database of a [Lychee](https://github.com/LycheeOrg/Lychee/) server and shows random pictures from it.

## Current Status

MVP!

Only SQLite is implemented for now (will be a small change to work with MySQL)

Configure the path of your database and the URL of your currently-running Lychee instance in `config.toml`, then run with `python app.py`