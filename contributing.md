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
export POSTGRES_DB=...
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

If you want to add new `msgid`s from a code file, use:
```shell
xgettext -d base -o locale/<any name>.pot bot/<name>.py --keyword=translator
```
Then insert new `msgid`s from the `.pot` file in the `.po` file and write theirs translations in `msgstr`.
Deleted all `.pot` files.

When you are finished, start generating a `.mo` file for each modified `.po` file:
```sh
msgfmt -o locale/<current_language_dir>/LC_MESSAGES/vtc-bot.mo locale/<current_language_dir>/LC_MESSAGES/vtc-bot.po"
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