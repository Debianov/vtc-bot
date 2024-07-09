[![Build Status](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml)

[Русская версия](./ru-readme.md)

# Functional

![functional](./docs/diagram.png)

# Install

## Database

Run `./scripts/setupdb.sh` for creating tables from `schema.sql`:
```sh
./setupdb.sh <db_name> <db_user> 
```

## The environment
Environment initialization:
```sh
poetry init
```
Install dependencies:
```sh
poetry install --only main
```

# Start
Create a secret file with the discord key, db name and username:
```sh
DISCORD_API_TOKEN=...
POSTGRES_DBNAME=...
POSTGRES_USER=...
```
And export it:
```sh
export file
```
Then:
```sh
poetry run bot
```
At starts with other ways it causes the import errors.

# Contributing
The project stack: discord.py, psycopg, pytest + dpytest. Check out our 
[contributing guidelines](./contributing.md) for ways to give feedback and contribute.

## Dev dependencies
```sh
poetry install --with dev,docs
```
## Docs generation
If you want a web version of the docs:
```sh
cd docs
make html
```