# How to contribute
Start by searching in the TODO and Backlog columns from the [project board](https://github.com/users/Debianov/projects/2). It is imperative that 
you work in your own fork.
When you are done, create new pull request. Keep in the mind that you should mention all the issues that were fixed.
Feel free to post any newbie topics in the `Discussion` tab.
# Dev dependencies
```sh
poetry install --with dev,docs
```
# Docs generation
If you want a web version of the docs:
```sh
cd docs
make html
```
# Start autotests
Create a secret file with the db name and username:
```sh
export POSTGRES_TEST_DBNAME=...
export POSTGRES_USER=...
```
And export it:
```sh
source file
```
Then:
```sh
poetry run pytest
```
Note that the working directory (`pwd`) must be `/project/`. Any other path will cause an error when starting pytest. 
# How to update locale
`locale` directory contains all the msgids for translating to the current language.
For updating to change a `.po` file in any dir of `locale`.
Then run
```sh
msgfmt -o locale/current_language_dir/LC_MESSAGES/vtc-bot.mo locale/current_language_dir/LC_MESSAGES/vtc-bot.po"
```
# How to get the DB up
Create a PostgreSQL database, then type
```shell
scripts/setupdb.sh <dbname> <postgresql_username>
```
If you want to update `schema.sql`, use
```shell
scripts/dumpdb.sh <dbname> <postgresql_username>
```
The script will automatically update `schema.sql`.